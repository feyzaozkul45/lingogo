import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from lessons import services as lesson_services
from lessons.models import Lesson

from .models import Quiz, QuizAttempt
from .services import score_submission


def quiz_view(request, slug):
    lesson = get_object_or_404(Lesson, slug=slug)
    quiz = get_object_or_404(
        Quiz.objects.prefetch_related('questions__choices'),
        lesson=lesson,
    )

    if request.method == 'POST':
        return _handle_submission(request, lesson, quiz)

    questions = []
    for question in quiz.questions.all():
        choices = list(question.choices.all())
        random.shuffle(choices)
        questions.append({'question': question, 'choices': choices})

    return render(request, 'quizzes/quiz.html', {
        'quiz': quiz,
        'lesson': lesson,
        'questions': questions,
        'has_scenario': hasattr(lesson, 'scenario'),
    })


def _handle_submission(request, lesson, quiz):
    results, score, total = score_submission(quiz.questions.all(), request.POST)

    if request.user.is_authenticated:
        attempt = QuizAttempt.objects.create(user=request.user, quiz=quiz, score=score, total=total)
        just_completed = lesson_services.sync_lesson_completion(request.user, lesson)
        request.session[f'quiz_result_{attempt.id}'] = {
            'results': results,
            'just_completed': just_completed,
        }
        return redirect('quizzes:result', attempt_id=attempt.id)

    return render(request, 'quizzes/result.html', {
        'quiz': quiz,
        'lesson': lesson,
        'score': score,
        'total': total,
        'results': results,
        'attempt': None,
        'just_completed': False,
        'has_scenario': hasattr(lesson, 'scenario'),
    })


@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related('quiz__lesson'),
        id=attempt_id,
        user=request.user,
    )
    session_data = request.session.pop(f'quiz_result_{attempt.id}', {})

    return render(request, 'quizzes/result.html', {
        'quiz': attempt.quiz,
        'lesson': attempt.quiz.lesson,
        'score': attempt.score,
        'total': attempt.total,
        'results': session_data.get('results'),
        'attempt': attempt,
        'just_completed': session_data.get('just_completed', False),
        'has_scenario': hasattr(attempt.quiz.lesson, 'scenario'),
    })
