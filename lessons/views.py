from django.shortcuts import get_object_or_404, render

from . import services
from .models import Lesson, LessonProgress, Scenario, ScenarioCompletion, Topic

VALID_LEVELS = {'A1', 'A2', 'B1', 'B2'}


def home(request):
    daily_topic = services.get_daily_topic()
    context = {
        'daily_topic': daily_topic,
        'daily_preview': services.get_daily_lesson_preview(daily_topic),
        'daily_words': services.get_daily_words(),
        'continue_lesson': services.get_continue_lesson(request.user),
        'topics': Topic.objects.filter(is_active=True).prefetch_related('lessons')[:4],
        'scenario_lessons': Lesson.objects.filter(scenario__isnull=False).select_related('topic', 'scenario')[:3],
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


def scenario_view(request, slug):
    lesson = get_object_or_404(Lesson.objects.select_related('topic'), slug=slug)
    scenario = get_object_or_404(
        Scenario.objects.prefetch_related('steps__options'),
        lesson=lesson,
    )

    if request.method == 'POST':
        just_completed = False
        needs_quiz = False
        if request.user.is_authenticated:
            ScenarioCompletion.objects.get_or_create(user=request.user, scenario=scenario)
            just_completed = services.sync_lesson_completion(request.user, lesson)
            if not just_completed:
                needs_quiz = not services.has_quiz_attempt(request.user, lesson)

        return render(request, 'lessons/scenario.html', {
            'lesson': lesson,
            'scenario': scenario,
            'show_complete': True,
            'just_completed': just_completed,
            'needs_quiz': needs_quiz,
        })

    steps_data = [
        {
            'speaker': step.speaker,
            'line': step.line,
            'line_tr': step.line_tr,
            'options': [
                {'text': option.text, 'correct': option.is_correct, 'feedback': option.feedback}
                for option in step.options.all()
            ],
        }
        for step in scenario.steps.all()
    ]

    return render(request, 'lessons/scenario.html', {
        'lesson': lesson,
        'scenario': scenario,
        'show_complete': False,
        'steps_data': steps_data,
    })
