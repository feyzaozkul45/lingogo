from django.contrib import admin

from .models import ExampleSentence, GrammarTip, Lesson, LessonProgress, Phrase, Topic, Word


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
