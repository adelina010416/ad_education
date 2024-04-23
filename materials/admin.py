from django.contrib import admin

from materials.models import Subject, Theme, Lesson, Comment


@admin.register(Subject)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('name',)


@admin.register(Theme)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'subject', 'owner', 'is_published',)
    list_filter = ('subject', 'owner', 'is_published',)
    search_fields = ('title',)


@admin.register(Lesson)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'theme', 'owner', 'is_published',)
    list_filter = ('theme', 'owner', 'is_published',)
    search_fields = ('title',)


@admin.register(Comment)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'user', 'theme', 'lesson',)
    list_filter = ('user', 'theme', 'lesson',)
    search_fields = ('text',)
