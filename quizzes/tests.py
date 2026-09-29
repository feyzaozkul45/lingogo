from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from lessons.models import Lesson, LessonProgress, Topic

from .models import Choice, Question, Quiz, QuizAttempt


class QuizScoringTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Icerik dosyalarindan bagimsiz, sentetik bir ders + quiz: bu sinif
        # sadece puanlama/tamamlama mekanigini test eder, hangi konularin
        # senaryosu oldugundan bagimsiz olmalidir.
        topic = Topic.objects.create(
            slug='quiz-test-topic', title='Test Topic', emoji='🧪', color='sun', level='A1', order=999,
        )
        cls.lesson = Lesson.objects.create(topic=topic, slug='quiz-test-lesson', title='Test Lesson', order=1)
        cls.quiz = Quiz.objects.create(lesson=cls.lesson, title='Test Quiz')
        for i in range(3):
            question = Question.objects.create(
                quiz=cls.quiz, question_type=Question.QuestionType.MULTIPLE_CHOICE, prompt=f'Question {i}', order=i,
            )
            Choice.objects.create(question=question, text='Correct answer', is_correct=True)
            Choice.objects.create(question=question, text='Wrong answer', is_correct=False)

    def _correct_answers(self):
        answers = {}
        for question in self.quiz.questions.all():
            correct = question.choices.get(is_correct=True)
            answers[f'question_{question.id}'] = correct.id
        return answers

    def test_anonymous_submission_scores_but_does_not_save(self):
        url = reverse('quizzes:quiz', kwargs={'slug': self.lesson.slug})
        total = self.quiz.questions.count()

        response = self.client.post(url, self._correct_answers())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'{total}/{total}')
        self.assertEqual(QuizAttempt.objects.count(), 0)
        self.assertEqual(LessonProgress.objects.count(), 0)

    def test_authenticated_submission_saves_attempt_and_completes_lesson(self):
        user = User.objects.create_user('quiz_tester', password='pass12345')
        self.client.force_login(user)
        url = reverse('quizzes:quiz', kwargs={'slug': self.lesson.slug})
        total = self.quiz.questions.count()

        response = self.client.post(url, self._correct_answers())

        attempt = QuizAttempt.objects.get(user=user, quiz=self.quiz)
        self.assertEqual(attempt.score, total)
        self.assertEqual(attempt.total, total)
        self.assertRedirects(response, reverse('quizzes:result', kwargs={'attempt_id': attempt.id}))
        self.assertTrue(LessonProgress.objects.filter(user=user, lesson=self.lesson).exists())

    def test_wrong_answer_is_scored_as_incorrect(self):
        user = User.objects.create_user('quiz_tester2', password='pass12345')
        self.client.force_login(user)
        url = reverse('quizzes:quiz', kwargs={'slug': self.lesson.slug})

        answers = self._correct_answers()
        first_key = next(iter(answers))
        question = self.quiz.questions.get(id=int(first_key.split('_')[1]))
        wrong_choice = question.choices.exclude(is_correct=True).first()
        answers[first_key] = wrong_choice.id

        self.client.post(url, answers)

        attempt = QuizAttempt.objects.get(user=user, quiz=self.quiz)
        self.assertEqual(attempt.score, self.quiz.questions.count() - 1)

    def test_other_users_cannot_view_someone_elses_result(self):
        owner = User.objects.create_user('owner', password='pass12345')
        intruder = User.objects.create_user('intruder', password='pass12345')
        attempt = QuizAttempt.objects.create(user=owner, quiz=self.quiz, score=1, total=6)

        self.client.force_login(intruder)
        response = self.client.get(reverse('quizzes:result', kwargs={'attempt_id': attempt.id}))

        self.assertEqual(response.status_code, 404)
