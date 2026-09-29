from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from quizzes.models import Question, Quiz, QuizAttempt

from . import services
from .models import Lesson, LessonProgress, ScenarioCompletion, ScenarioOption, ScenarioStep, Topic, Word


class LoadContentCommandTests(TestCase):
    def test_load_content_creates_expected_objects(self):
        call_command('load_content')

        self.assertEqual(Topic.objects.count(), 20)
        self.assertEqual(Lesson.objects.count(), 20)
        self.assertTrue(Word.objects.filter(lesson__topic__slug='cafe').exists())
        self.assertTrue(Quiz.objects.filter(lesson__topic__slug='restaurant').exists())

    def test_load_content_is_idempotent(self):
        call_command('load_content')
        first_topics = Topic.objects.count()
        first_words = Word.objects.count()
        first_questions = Question.objects.count()

        call_command('load_content')

        self.assertEqual(Topic.objects.count(), first_topics)
        self.assertEqual(Word.objects.count(), first_words)
        self.assertEqual(Question.objects.count(), first_questions)

    def test_load_content_creates_scenario_for_restaurant(self):
        call_command('load_content')

        lesson = Lesson.objects.get(slug='restaurant-basics')

        self.assertTrue(hasattr(lesson, 'scenario'))
        self.assertGreaterEqual(lesson.scenario.steps.count(), 4)
        self.assertTrue(all(step.options.count() >= 2 for step in lesson.scenario.steps.all()))
        self.assertTrue(all(step.options.filter(is_correct=True).exists() for step in lesson.scenario.steps.all()))

    def test_load_content_scenario_is_idempotent(self):
        call_command('load_content')
        first_step_count = ScenarioStep.objects.count()
        first_option_count = ScenarioOption.objects.count()

        call_command('load_content')

        self.assertEqual(ScenarioStep.objects.count(), first_step_count)
        self.assertEqual(ScenarioOption.objects.count(), first_option_count)


class LessonCompletionRuleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('load_content')
        cls.restaurant_lesson = Lesson.objects.get(slug='restaurant-basics')  # senaryolu
        cls.cafe_lesson = Lesson.objects.get(slug='cafe-basics')  # senaryosuz

    def setUp(self):
        self.user = User.objects.create_user('learner', password='pass12345')

    def test_quiz_alone_completes_lesson_without_scenario(self):
        quiz = Quiz.objects.get(lesson=self.cafe_lesson)
        QuizAttempt.objects.create(user=self.user, quiz=quiz, score=5, total=5)

        created = services.sync_lesson_completion(self.user, self.cafe_lesson)

        self.assertTrue(created)
        self.assertTrue(LessonProgress.objects.filter(user=self.user, lesson=self.cafe_lesson).exists())

    def test_quiz_alone_does_not_complete_lesson_with_scenario(self):
        quiz = Quiz.objects.get(lesson=self.restaurant_lesson)
        QuizAttempt.objects.create(user=self.user, quiz=quiz, score=5, total=5)

        created = services.sync_lesson_completion(self.user, self.restaurant_lesson)

        self.assertFalse(created)
        self.assertFalse(LessonProgress.objects.filter(user=self.user, lesson=self.restaurant_lesson).exists())

    def test_scenario_alone_does_not_complete_lesson(self):
        ScenarioCompletion.objects.create(user=self.user, scenario=self.restaurant_lesson.scenario)

        created = services.sync_lesson_completion(self.user, self.restaurant_lesson)

        self.assertFalse(created)
        self.assertFalse(LessonProgress.objects.filter(user=self.user, lesson=self.restaurant_lesson).exists())

    def test_quiz_and_scenario_together_complete_lesson(self):
        quiz = Quiz.objects.get(lesson=self.restaurant_lesson)
        QuizAttempt.objects.create(user=self.user, quiz=quiz, score=5, total=5)
        ScenarioCompletion.objects.create(user=self.user, scenario=self.restaurant_lesson.scenario)

        created = services.sync_lesson_completion(self.user, self.restaurant_lesson)

        self.assertTrue(created)
        self.assertTrue(LessonProgress.objects.filter(user=self.user, lesson=self.restaurant_lesson).exists())

    def test_sync_never_deletes_an_existing_progress_record(self):
        # Ders, senaryo eklenmeden once (veya baska bir sebeple) zaten tamamlanmis olsun.
        LessonProgress.objects.create(user=self.user, lesson=self.restaurant_lesson)

        # Ne quiz ne senaryo kosulu saglanmasa bile mevcut kayit silinmemeli.
        created = services.sync_lesson_completion(self.user, self.restaurant_lesson)

        self.assertFalse(created)
        self.assertTrue(LessonProgress.objects.filter(user=self.user, lesson=self.restaurant_lesson).exists())
        self.assertEqual(LessonProgress.objects.filter(user=self.user, lesson=self.restaurant_lesson).count(), 1)


class ScenarioViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('load_content')
        cls.lesson = Lesson.objects.get(slug='restaurant-basics')
        cls.cafe_lesson = Lesson.objects.get(slug='cafe-basics')

    def test_scenario_page_renders_steps(self):
        url = reverse('lessons:scenario', kwargs={'slug': self.lesson.slug})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Are you ready to order?')

    def test_lesson_without_scenario_returns_404(self):
        url = reverse('lessons:scenario', kwargs={'slug': self.cafe_lesson.slug})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_anonymous_completion_post_does_not_persist(self):
        url = reverse('lessons:scenario', kwargs={'slug': self.lesson.slug})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ScenarioCompletion.objects.count(), 0)
        self.assertContains(response, 'kayıt ol')

    def test_authenticated_completion_with_prior_quiz_completes_lesson(self):
        user = User.objects.create_user('scenario_tester', password='pass12345')
        self.client.force_login(user)
        quiz = Quiz.objects.get(lesson=self.lesson)
        QuizAttempt.objects.create(user=user, quiz=quiz, score=5, total=5)

        url = reverse('lessons:scenario', kwargs={'slug': self.lesson.slug})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ScenarioCompletion.objects.filter(user=user, scenario=self.lesson.scenario).exists())
        self.assertTrue(LessonProgress.objects.filter(user=user, lesson=self.lesson).exists())
        self.assertContains(response, 'Dersi tamamladın')

    def test_authenticated_completion_without_quiz_hints_at_quiz(self):
        user = User.objects.create_user('scenario_tester2', password='pass12345')
        self.client.force_login(user)

        url = reverse('lessons:scenario', kwargs={'slug': self.lesson.slug})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ScenarioCompletion.objects.filter(user=user, scenario=self.lesson.scenario).exists())
        self.assertFalse(LessonProgress.objects.filter(user=user, lesson=self.lesson).exists())
        self.assertContains(response, "quiz'i de çöz")
