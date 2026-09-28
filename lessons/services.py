from datetime import date

from .models import Lesson, LessonProgress, Topic, Word


def get_daily_topic():
    """Tarihe göre deterministik olarak seçilen 'günün konusu'."""
    topics = list(Topic.objects.filter(is_active=True))
    if not topics:
        return None
    index = date.today().toordinal() % len(topics)
    return topics[index]


def get_daily_words(count=5):
    """Tarihe göre seçilen, sabit sayıda günlük kelime."""
    words = list(Word.objects.select_related('lesson').all())
    if not words:
        return []
    start = date.today().toordinal() % len(words)
    rotated = words[start:] + words[:start]
    return rotated[:count]


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


def get_progress_stats(user):
    from quizzes.models import QuizAttempt

    completed_lessons = LessonProgress.objects.filter(user=user).select_related('lesson', 'lesson__topic')
    lessons_completed = completed_lessons.count()
    words_learned = Word.objects.filter(lesson__progress_entries__user=user).count()
    attempts = QuizAttempt.objects.filter(user=user).select_related('quiz__lesson')
    quizzes_completed = attempts.values('quiz').distinct().count()

    return {
        'lessons_completed': lessons_completed,
        'words_learned': words_learned,
        'quizzes_completed': quizzes_completed,
        'completed_lessons': completed_lessons,
        'recent_attempts': attempts[:10],
    }
