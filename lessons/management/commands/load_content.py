import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from lessons.models import (
    ExampleSentence,
    GrammarTip,
    Lesson,
    Phrase,
    Scenario,
    ScenarioOption,
    ScenarioStep,
    Topic,
    Word,
)
from quizzes.models import Choice, Question, Quiz


class Command(BaseCommand):
    help = "content/ altındaki JSON dosyalarını veritabanına yükler (idempotent)."

    def handle(self, *args, **options):
        content_dir = Path(settings.BASE_DIR) / 'content'
        json_files = sorted(content_dir.glob('**/*.json'))

        if not json_files:
            self.stdout.write(self.style.WARNING('content/ altında JSON dosyası bulunamadı.'))
            return

        for path in json_files:
            data = json.loads(path.read_text(encoding='utf-8'))
            self.load_file(data)
            self.stdout.write(self.style.SUCCESS(f'Yüklendi: {path.relative_to(settings.BASE_DIR)}'))

    def load_file(self, data):
        topic_data = data['topic']
        topic, _ = Topic.objects.update_or_create(
            slug=topic_data['slug'],
            defaults={
                'title': topic_data['title'],
                'emoji': topic_data['emoji'],
                'color': topic_data['color'],
                'description': topic_data.get('description', ''),
                'level': topic_data['level'],
                'order': topic_data.get('order', 0),
                'is_active': topic_data.get('is_active', True),
            },
        )

        lesson_data = data['lesson']
        lesson, _ = Lesson.objects.update_or_create(
            slug=lesson_data['slug'],
            defaults={
                'topic': topic,
                'title': lesson_data['title'],
                'intro': lesson_data.get('intro', ''),
                'order': lesson_data.get('order', 0),
            },
        )

        self._sync_words(lesson, data.get('words', []))
        self._sync_phrases(lesson, data.get('phrases', []))
        self._sync_grammar(lesson, data.get('grammar', []))
        self._sync_examples(lesson, data.get('examples', []))

        if 'quiz' in data:
            self._sync_quiz(lesson, data['quiz'])

        if 'scenario' in data:
            self._sync_scenario(lesson, data['scenario'])

    def _sync_words(self, lesson, items):
        lesson.words.all().delete()
        for order, item in enumerate(items):
            Word.objects.create(
                lesson=lesson,
                english=item['english'],
                turkish=item['turkish'],
                example_en=item.get('example_en', ''),
                example_tr=item.get('example_tr', ''),
                order=order,
            )

    def _sync_phrases(self, lesson, items):
        lesson.phrases.all().delete()
        for order, item in enumerate(items):
            Phrase.objects.create(
                lesson=lesson,
                english=item['english'],
                turkish=item['turkish'],
                note=item.get('note', ''),
                order=order,
            )

    def _sync_grammar(self, lesson, items):
        lesson.grammar_tips.all().delete()
        for order, item in enumerate(items):
            GrammarTip.objects.create(
                lesson=lesson,
                title=item['title'],
                explanation=item['explanation'],
                examples='\n'.join(item.get('examples', [])),
                order=order,
            )

    def _sync_examples(self, lesson, items):
        lesson.example_sentences.all().delete()
        for order, item in enumerate(items):
            ExampleSentence.objects.create(
                lesson=lesson,
                english=item['english'],
                turkish=item['turkish'],
                order=order,
            )

    def _sync_quiz(self, lesson, quiz_data):
        quiz, _ = Quiz.objects.update_or_create(
            lesson=lesson,
            defaults={'title': quiz_data['title']},
        )
        quiz.questions.all().delete()
        for order, q in enumerate(quiz_data.get('questions', [])):
            question = Question.objects.create(
                quiz=quiz,
                question_type=q['type'],
                prompt=q['prompt'],
                explanation=q.get('explanation', ''),
                order=order,
            )
            for choice in q.get('choices', []):
                Choice.objects.create(
                    question=question,
                    text=choice['text'],
                    is_correct=choice.get('correct', False),
                )

    def _sync_scenario(self, lesson, scenario_data):
        scenario, _ = Scenario.objects.update_or_create(
            lesson=lesson,
            defaults={
                'title': scenario_data['title'],
                'setting': scenario_data.get('setting', ''),
                'task': scenario_data.get('task', ''),
            },
        )
        scenario.steps.all().delete()
        for order, step_data in enumerate(scenario_data.get('steps', [])):
            step = ScenarioStep.objects.create(
                scenario=scenario,
                speaker=step_data['speaker'],
                line=step_data['line'],
                line_tr=step_data.get('line_tr', ''),
                order=order,
            )
            for option in step_data.get('options', []):
                ScenarioOption.objects.create(
                    step=step,
                    text=option['text'],
                    is_correct=option.get('correct', False),
                    feedback=option.get('feedback', ''),
                )
