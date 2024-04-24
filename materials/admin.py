from django.contrib import admin

from materials.models import Subject, Theme, Lesson, TestPaper, \
    Question, Answer, Result


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Регистрация модели Subject в админке"""
    list_display = ('id', 'name',)
    search_fields = ('name',)


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    """Регистрация модели Theme в админке"""
    list_display = ('id', 'title', 'subject', 'owner', 'is_published',)
    list_filter = ('subject', 'owner', 'is_published',)
    search_fields = ('title',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Регистрация модели Lesson в админке"""
    list_display = ('id', 'title', 'theme', 'owner', 'is_published',)
    list_filter = ('theme', 'owner', 'is_published',)
    search_fields = ('title',)


@admin.register(TestPaper)
class TestPaperAdmin(admin.ModelAdmin):
    """Регистрация модели TestPaper в админке"""
    list_display = ('id', 'title', 'theme', 'owner', 'is_published',)
    search_fields = ('theme',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Регистрация модели Question в админке"""
    list_display = ('id', 'question_text', 'test',)
    search_fields = ('question_text',)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Регистрация модели Answer в админке"""
    list_display = ('id', 'answer_text', 'is_correct', 'question',)
    list_filter = ('is_correct', 'question',)
    search_fields = ('answer_text',)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    """Регистрация модели Result в админке"""
    list_display = ('id', 'test', 'user',)
