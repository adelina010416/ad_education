from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Регистрация модели User в админке"""
    list_display = ('id', 'email', 'is_staff',)
    list_filter = ('is_active', 'is_staff',)
    search_fields = ('email',)
