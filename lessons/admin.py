from django.contrib import admin

from .models import (
    ExampleSentence,
    GrammarTip,
    Lesson,
    LessonProgress,
    Phrase,
    ReadingAttempt,
    ReadingText,
    Scenario,
    ScenarioCompletion,
    ScenarioOption,
    ScenarioStep,
    Topic,
    Word,
)


class WordInline(admin.TabularInline):
    model = Word
    extra = 1


class PhraseInline(admin.TabularInline):
    model = Phrase
    extra = 1


class GrammarTipInline(admin.StackedInline):
    model = GrammarTip
    extra = 0


class ExampleSentenceInline(admin.TabularInline):
    model = ExampleSentence
    extra = 1


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('emoji', 'title', 'slug', 'level', 'order', 'is_active')
    list_filter = ('level', 'is_active')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'order')
    list_filter = ('topic',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = [WordInline, PhraseInline, GrammarTipInline, ExampleSentenceInline]


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed_at')
    list_filter = ('lesson__topic',)


class ScenarioOptionInline(admin.TabularInline):
    model = ScenarioOption
    extra = 2


class ScenarioStepInline(admin.StackedInline):
    model = ScenarioStep
    extra = 0


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson')
    inlines = [ScenarioStepInline]


@admin.register(ScenarioStep)
class ScenarioStepAdmin(admin.ModelAdmin):
    list_display = ('speaker', 'line', 'scenario', 'order')
    list_filter = ('scenario',)
    inlines = [ScenarioOptionInline]


@admin.register(ScenarioCompletion)
class ScenarioCompletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'scenario', 'completed_at')
    list_filter = ('scenario__lesson__topic',)


@admin.register(ReadingText)
class ReadingTextAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'slug', 'is_active')
    list_filter = ('level', 'is_active')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(ReadingAttempt)
class ReadingAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'reading_text', 'score', 'total', 'created_at')
    list_filter = ('reading_text__level',)
