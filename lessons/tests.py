from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from quizzes.models import Question, Quiz, QuizAttempt

from . import services
from .models import (
    Lesson,
    LessonProgress,
    ReadingAttempt,
    ReadingText,
    ScenarioCompletion,
    ScenarioOption,
    ScenarioStep,
    Topic,
    Word,
)

READING_WORD_RANGES = {
    'A1': (60, 80),
    'A2': (100, 120),
    'B1': (150, 180),
    'B2': (200, 250),
}


def create_lesson_without_scenario(slug='test-lesson-no-scenario', with_quiz=True):
    """Icerik dosyalarindan bagimsiz, senaryosu olmayan bir ders olusturur.

    Gercek konularin hepsi zamanla senaryo kazanabildigi icin, 'senaryosu
    olmayan ders' davranisini test etmek gercek bir slug'a (ör. cafe-basics)
    degil, bu sentetik derse dayanir.
    """
    topic = Topic.objects.create(
        slug=f'{slug}-topic', title='Test Topic', emoji='🧪', color='sun', level='A1', order=999,
    )
    lesson = Lesson.objects.create(topic=topic, slug=slug, title='Test Lesson', order=1)
    if with_quiz:
        Quiz.objects.create(lesson=lesson, title='Test Quiz')
    return lesson


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
        cls.no_scenario_lesson = create_lesson_without_scenario()

    def setUp(self):
        self.user = User.objects.create_user('learner', password='pass12345')

    def test_quiz_alone_completes_lesson_without_scenario(self):
        quiz = Quiz.objects.get(lesson=self.no_scenario_lesson)
        QuizAttempt.objects.create(user=self.user, quiz=quiz, score=5, total=5)

        created = services.sync_lesson_completion(self.user, self.no_scenario_lesson)

        self.assertTrue(created)
        self.assertTrue(LessonProgress.objects.filter(user=self.user, lesson=self.no_scenario_lesson).exists())

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
        cls.no_scenario_lesson = create_lesson_without_scenario(slug='test-lesson-no-scenario-2', with_quiz=False)

    def test_scenario_page_renders_steps(self):
        url = reverse('lessons:scenario', kwargs={'slug': self.lesson.slug})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Are you ready to order?')

    def test_lesson_without_scenario_returns_404(self):
        url = reverse('lessons:scenario', kwargs={'slug': self.no_scenario_lesson.slug})

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


class ReadingContentTests(TestCase):
    def test_load_content_creates_reading_texts(self):
        call_command('load_content')

        self.assertGreaterEqual(ReadingText.objects.count(), 2)
        self.assertTrue(ReadingText.objects.filter(slug='a1-morning-routine').exists())
        self.assertTrue(ReadingText.objects.filter(slug='b2-remote-work').exists())

    def test_load_content_reading_is_idempotent(self):
        call_command('load_content')
        first_count = ReadingText.objects.count()
        first_question_count = Question.objects.filter(reading_text__isnull=False).count()

        call_command('load_content')

        self.assertEqual(ReadingText.objects.count(), first_count)
        self.assertEqual(Question.objects.filter(reading_text__isnull=False).count(), first_question_count)

    def test_reading_word_counts_are_within_level_range(self):
        call_command('load_content')

        for reading in ReadingText.objects.all():
            lo, hi = READING_WORD_RANGES[reading.level]
            count = reading.word_count()
            self.assertTrue(
                lo <= count <= hi,
                f'{reading.slug} ({reading.level}): {count} kelime, beklenen aralık [{lo}, {hi}]',
            )

    def test_reading_texts_have_exactly_three_questions(self):
        call_command('load_content')

        for reading in ReadingText.objects.all():
            self.assertEqual(
                reading.questions.count(), 3,
                f'{reading.slug}: {reading.questions.count()} soru, 3 bekleniyordu',
            )
            for question in reading.questions.all():
                self.assertEqual(question.choices.count(), 3)
                self.assertEqual(question.choices.filter(is_correct=True).count(), 1)


class ReadingViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('load_content')
        cls.reading = ReadingText.objects.get(slug='a1-morning-routine')

    def _correct_answers(self):
        answers = {}
        for question in self.reading.questions.all():
            correct = question.choices.get(is_correct=True)
            answers[f'question_{question.id}'] = correct.id
        return answers

    def test_reading_list_shows_texts(self):
        response = self.client.get(reverse('lessons:reading_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Morning Routine')

    def test_reading_list_filters_by_level(self):
        response = self.client.get(reverse('lessons:reading_list'), {'level': 'B2'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The Rise of Remote Work')
        self.assertNotContains(response, 'My Morning Routine')

    def test_reading_detail_renders_text_and_questions(self):
        response = self.client.get(reverse('lessons:reading_detail', kwargs={'slug': self.reading.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'wake up at seven')

    def test_anonymous_submission_scores_but_does_not_persist(self):
        url = reverse('lessons:reading_detail', kwargs={'slug': self.reading.slug})

        response = self.client.post(url, self._correct_answers())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '3/3')
        self.assertEqual(ReadingAttempt.objects.count(), 0)
        self.assertContains(response, 'kayıt ol')

    def test_authenticated_submission_persists_and_updates_progress_stats(self):
        user = User.objects.create_user('reading_tester', password='pass12345')
        self.client.force_login(user)
        url = reverse('lessons:reading_detail', kwargs={'slug': self.reading.slug})

        response = self.client.post(url, self._correct_answers())

        attempt = ReadingAttempt.objects.get(user=user, reading_text=self.reading)
        self.assertEqual(attempt.score, 3)
        self.assertEqual(attempt.total, 3)
        self.assertRedirects(response, reverse('lessons:reading_result', kwargs={'attempt_id': attempt.id}))

        stats = services.get_progress_stats(user)
        self.assertEqual(stats['readings_completed'], 1)

    def test_other_users_cannot_view_someone_elses_reading_result(self):
        owner = User.objects.create_user('reading_owner', password='pass12345')
        intruder = User.objects.create_user('reading_intruder', password='pass12345')
        attempt = ReadingAttempt.objects.create(user=owner, reading_text=self.reading, score=2, total=3)

        self.client.force_login(intruder)
        response = self.client.get(reverse('lessons:reading_result', kwargs={'attempt_id': attempt.id}))

        self.assertEqual(response.status_code, 404)
