from datetime import date

from .models import Lesson, LessonProgress, ReadingAttempt, ScenarioCompletion, Topic, Word


def get_daily_topic():
    """Tarihe göre deterministik olarak seçilen 'günün konusu'."""
    topics = list(Topic.objects.filter(is_active=True))
    if not topics:
        return None
    index = date.today().toordinal() % len(topics)
    return topics[index]


def get_daily_words(count=5, level=None):
    """Tarihe göre seçilen, sabit sayıda günlük kelime.

    `level` verilirse (günün konusunun seviyesi) kelimeler sadece o seviyedeki
    konulardan seçilir; o seviyede hiç kelime yoksa tüm kelimelere düşülür.
    """
    words = Word.objects.select_related('lesson')
    if level:
        words = words.filter(lesson__topic__level=level) or Word.objects.select_related('lesson')
    words = list(words)
    if not words:
        return []
    start = date.today().toordinal() % len(words)
    rotated = words[start:] + words[:start]
    return rotated[:count]


def get_daily_lesson_preview(topic):
    """Günün konusu kartı için önizleme verisi: ders, örnek ifadeler, kelime sayısı, tahmini süre."""
    if not topic:
        return None
    lesson = topic.lessons.prefetch_related('phrases', 'words').first()
    if not lesson:
        return None
    words = lesson.words.all()
    phrases = lesson.phrases.all()
    minutes = max(3, round((len(words) + len(phrases)) * 0.5))
    return {
        'lesson': lesson,
        'phrases': list(phrases)[:3],
        'word_count': len(words),
        'minutes': minutes,
    }


def get_continue_lesson(user):
    """Giriş yapmış kullanıcı için tamamlanmamış ilk ders; yapılmamışsa ilk ders."""
    lessons = Lesson.objects.select_related('topic').order_by('topic__order', 'order')
    if user.is_authenticated:
        completed_ids = LessonProgress.objects.filter(user=user).values_list('lesson_id', flat=True)
        lessons = lessons.exclude(id__in=completed_ids)
    return lessons.first()


def get_completed_topic_ids(user):
    if not user.is_authenticated:
        return set()
    return set(
        Topic.objects.filter(lessons__progress_entries__user=user).values_list('id', flat=True)
    )


def has_quiz_attempt(user, lesson):
    from quizzes.models import QuizAttempt

    return QuizAttempt.objects.filter(user=user, quiz__lesson=lesson).exists()


def sync_lesson_completion(user, lesson):
    """Quiz + (varsa) senaryo tamamlaninca LessonProgress olusturur.

    Sadece olusturur, asla mevcut bir LessonProgress kaydini silmez ya da
    geri almaz — senaryosu sonradan eklenen bir ders, daha once sadece
    quiz ile tamamlanmis olsa bile tamamlanmis sayilmaya devam eder.
    """
    if not user.is_authenticated:
        return False

    if not has_quiz_attempt(user, lesson):
        return False

    scenario = getattr(lesson, 'scenario', None)
    if scenario is not None and not ScenarioCompletion.objects.filter(user=user, scenario=scenario).exists():
        return False

    _, created = LessonProgress.objects.get_or_create(user=user, lesson=lesson)
    return created


def get_progress_stats(user):
    from quizzes.models import QuizAttempt

    completed_lessons = LessonProgress.objects.filter(user=user).select_related('lesson', 'lesson__topic')
    lessons_completed = completed_lessons.count()
    words_learned = Word.objects.filter(lesson__progress_entries__user=user).count()
    attempts = QuizAttempt.objects.filter(user=user).select_related('quiz__lesson')
    quizzes_completed = attempts.values('quiz').distinct().count()
    readings_completed = ReadingAttempt.objects.filter(user=user).values('reading_text').distinct().count()

    return {
        'lessons_completed': lessons_completed,
        'words_learned': words_learned,
        'quizzes_completed': quizzes_completed,
        'readings_completed': readings_completed,
        'completed_lessons': completed_lessons,
        'recent_attempts': attempts[:10],
    }
