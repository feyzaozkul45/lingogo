from django.shortcuts import get_object_or_404, render

from . import services
from .models import Lesson, LessonProgress, Topic

VALID_LEVELS = {'A1', 'A2', 'B1', 'B2'}


def home(request):
    context = {
        'daily_topic': services.get_daily_topic(),
        'daily_words': services.get_daily_words(),
        'continue_lesson': services.get_continue_lesson(request.user),
        'topics': Topic.objects.filter(is_active=True)[:4],
    }
    return render(request, 'home.html', context)


def topic_list(request):
    level = request.GET.get('level')
    topics = Topic.objects.filter(is_active=True).prefetch_related('lessons')
    if level in VALID_LEVELS:
        topics = topics.filter(level=level)

    context = {
        'topics': topics,
        'selected_level': level if level in VALID_LEVELS else None,
        'levels': sorted(VALID_LEVELS),
        'completed_topic_ids': services.get_completed_topic_ids(request.user),
    }
    return render(request, 'lessons/topic_list.html', context)


def lesson_detail(request, slug):
    lesson = get_object_or_404(
        Lesson.objects.select_related('topic').prefetch_related(
            'words', 'phrases', 'grammar_tips', 'example_sentences'
        ),
        slug=slug,
    )
    is_completed = False
    if request.user.is_authenticated:
        is_completed = LessonProgress.objects.filter(user=request.user, lesson=lesson).exists()

    has_grammar = bool(lesson.grammar_tips.all())
    total_steps = 3 + (1 if has_grammar else 0)  # kelimeler, ifadeler, [grammar], ornek cumleler

    context = {
        'lesson': lesson,
        'is_completed': is_completed,
        'has_quiz': hasattr(lesson, 'quiz'),
        'has_grammar': has_grammar,
        'total_steps': total_steps,
    }
    return render(request, 'lessons/lesson_detail.html', context)
