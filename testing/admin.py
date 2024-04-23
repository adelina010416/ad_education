from django.contrib import admin

from testing.models import TestPaper, Question, Answer, Result


@admin.register(TestPaper)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'theme', 'owner', 'is_published',)
    search_fields = ('theme',)


@admin.register(Question)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_text', 'test',)
    search_fields = ('question_text',)


@admin.register(Answer)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'answer_text', 'is_correct', 'question',)
    list_filter = ('is_correct', 'question',)
    search_fields = ('answer_text',)


@admin.register(Result)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'test', 'user',)
