import random
import re

from django.shortcuts import get_object_or_404, redirect, render

from quizzes.services import score_submission

from . import services
from .models import Lesson, LessonProgress, ReadingAttempt, ReadingText, Scenario, ScenarioCompletion, Topic

VALID_LEVELS = {'A1', 'A2', 'B1', 'B2'}


def home(request):
    daily_topic = services.get_daily_topic()
    context = {
        'daily_topic': daily_topic,
        'daily_preview': services.get_daily_lesson_preview(daily_topic),
        'daily_words': services.get_daily_words(level=daily_topic.level if daily_topic else None),
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
        'has_scenario': hasattr(lesson, 'scenario'),
        'has_grammar': has_grammar,
        'total_steps': total_steps,
    }
    return render(request, 'lessons/lesson_detail.html', context)


def scenario_list(request):
    level = request.GET.get('level')
    lessons = Lesson.objects.filter(scenario__isnull=False).select_related('topic', 'scenario').order_by(
        'topic__level', 'topic__order', 'order'
    )
    if level in VALID_LEVELS:
        lessons = lessons.filter(topic__level=level)

    completed_scenario_ids = set()
    if request.user.is_authenticated:
        completed_scenario_ids = set(
            ScenarioCompletion.objects.filter(user=request.user).values_list('scenario_id', flat=True)
        )

    context = {
        'lessons': lessons,
        'selected_level': level if level in VALID_LEVELS else None,
        'levels': sorted(VALID_LEVELS),
        'completed_scenario_ids': completed_scenario_ids,
    }
    return render(request, 'lessons/scenario_list.html', context)


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


def reading_list(request):
    level = request.GET.get('level')
    readings = ReadingText.objects.filter(is_active=True)
    if level in VALID_LEVELS:
        readings = readings.filter(level=level)

    completed_reading_ids = set()
    if request.user.is_authenticated:
        completed_reading_ids = set(
            ReadingAttempt.objects.filter(user=request.user).values_list('reading_text_id', flat=True)
        )

    context = {
        'readings': readings,
        'selected_level': level if level in VALID_LEVELS else None,
        'levels': sorted(VALID_LEVELS),
        'completed_reading_ids': completed_reading_ids,
    }
    return render(request, 'lessons/reading_list.html', context)


def reading_detail(request, slug):
    reading = get_object_or_404(
        ReadingText.objects.prefetch_related('questions__choices'),
        slug=slug,
        is_active=True,
    )

    if request.method == 'POST':
        results, score, total = score_submission(reading.questions.all(), request.POST)

        if request.user.is_authenticated:
            attempt = ReadingAttempt.objects.create(user=request.user, reading_text=reading, score=score, total=total)
            request.session[f'reading_result_{attempt.id}'] = {'results': results}
            return redirect('lessons:reading_result', attempt_id=attempt.id)

        return render(request, 'lessons/reading_result.html', {
            'reading': reading,
            'score': score,
            'total': total,
            'results': results,
            'attempt': None,
        })

    questions = []
    for question in reading.questions.all():
        choices = list(question.choices.all())
        random.shuffle(choices)
        questions.append({'question': question, 'choices': choices})

    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', reading.english_text) if p.strip()]

    return render(request, 'lessons/reading_detail.html', {
        'reading': reading,
        'paragraphs': paragraphs,
        'questions': questions,
    })


def reading_result(request, attempt_id):
    attempt = get_object_or_404(
        ReadingAttempt.objects.select_related('reading_text'),
        id=attempt_id,
        user=request.user,
    )
    session_data = request.session.pop(f'reading_result_{attempt.id}', {})

    return render(request, 'lessons/reading_result.html', {
        'reading': attempt.reading_text,
        'score': attempt.score,
        'total': attempt.total,
        'results': session_data.get('results'),
        'attempt': attempt,
    })
