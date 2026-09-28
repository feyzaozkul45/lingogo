from django.core.management import call_command
from django.test import TestCase

from quizzes.models import Question, Quiz

from .models import Lesson, Topic, Word


class LoadContentCommandTests(TestCase):
    def test_load_content_creates_expected_objects(self):
        call_command('load_content')

        self.assertEqual(Topic.objects.count(), 5)
        self.assertEqual(Lesson.objects.count(), 5)
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
