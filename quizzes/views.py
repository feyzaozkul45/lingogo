import random

from django.shortcuts import get_object_or_404, redirect, render

from lessons.models import Lesson, LessonProgress

from .models import Quiz, QuizAttempt


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
    })


def _handle_submission(request, lesson, quiz):
    results = []
    score = 0

    for question in quiz.questions.all():
        choices = list(question.choices.all())
        selected_id = request.POST.get(f'question_{question.id}')
        selected_choice = next((c for c in choices if str(c.id) == selected_id), None)
        correct_choice = next((c for c in choices if c.is_correct), None)
        is_correct = bool(selected_choice and selected_choice.is_correct)

        if is_correct:
            score += 1

        results.append({
            'prompt': question.prompt,
            'explanation': question.explanation,
            'is_correct': is_correct,
            'selected_text': selected_choice.text if selected_choice else None,
            'correct_text': correct_choice.text if correct_choice else None,
        })

    total = quiz.questions.count()

    if request.user.is_authenticated:
        attempt = QuizAttempt.objects.create(user=request.user, quiz=quiz, score=score, total=total)
        _, just_completed = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
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
    })


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
    })
