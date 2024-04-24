from django.contrib import admin

from comments.models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Регистрация модели Comment в админке"""
    list_display = ('id', 'text', 'user', 'theme', 'lesson',)
    list_filter = ('user', 'theme', 'lesson',)
    search_fields = ('text',)
