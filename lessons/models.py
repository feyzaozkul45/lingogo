from django.conf import settings
from django.db import models


class Topic(models.Model):
    class Level(models.TextChoices):
        A1 = 'A1', 'A1'
        A2 = 'A2', 'A2'
        B1 = 'B1', 'B1'
        B2 = 'B2', 'B2'

    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    emoji = models.CharField(max_length=10)
    color = models.CharField(max_length=20)
    description = models.CharField(max_length=255, blank=True)
    level = models.CharField(max_length=2, choices=Level.choices)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class Lesson(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    intro = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class Word(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='words')
    english = models.CharField(max_length=100)
    turkish = models.CharField(max_length=150)
    example_en = models.CharField(max_length=255, blank=True)
    example_tr = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.english


class Phrase(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='phrases')
    english = models.CharField(max_length=255)
    turkish = models.CharField(max_length=255)
    note = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.english


class GrammarTip(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='grammar_tips')
    title = models.CharField(max_length=100)
    explanation = models.TextField()
    examples = models.TextField(blank=True, help_text='Her satır bir örnek cümle')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title

    def example_list(self):
        return [line.strip() for line in self.examples.splitlines() if line.strip()]


class ExampleSentence(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='example_sentences')
    english = models.CharField(max_length=255)
    turkish = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.english


class Scenario(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='scenario')
    title = models.CharField(max_length=150)
    setting = models.CharField(max_length=255)
    task = models.CharField(max_length=255, help_text='Ders sonu küçük görev')

    def __str__(self):
        return self.title


class ScenarioStep(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name='steps')
    speaker = models.CharField(max_length=100)
    line = models.CharField(max_length=255)
    line_tr = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.speaker}: {self.line}'


class ScenarioOption(models.Model):
    step = models.ForeignKey(ScenarioStep, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    feedback = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.text


class ScenarioCompletion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scenario_completions')
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name='completions')
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'scenario'], name='unique_user_scenario_completion'),
        ]

    def __str__(self):
        return f'{self.user} — {self.scenario}'


class LessonProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress_entries')
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'lesson'], name='unique_user_lesson_progress'),
        ]

    def __str__(self):
        return f'{self.user} — {self.lesson}'
