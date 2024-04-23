from django.db import models

from constants import nullable
# from testing.models import TestPaper
from users.models import User


class Subject(models.Model):
    """Предмет"""
    name = models.CharField(max_length=50, unique=True, verbose_name='название')
    description = models.TextField(max_length=250, **nullable, verbose_name='описание')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'предмет'
        verbose_name_plural = 'предметы'


class Theme(models.Model):
    """Тема урока"""
    title = models.CharField(max_length=250, verbose_name='название')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='предмет')
    description = models.TextField(max_length=250, **nullable, verbose_name='описание')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, **nullable, verbose_name='владелец')
    is_published = models.BooleanField(default=False, verbose_name='признак публикации')

    def __str__(self):
        return f'Тема по предмету "{self.subject}": {self.title}'

    class Meta:
        verbose_name = 'тема'
        verbose_name_plural = 'темы'
        permissions = [
            ('set_published',
             'Can publish theme')
        ]


class Lesson(models.Model):
    """Урок"""
    title = models.CharField(max_length=250, verbose_name='название')
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, verbose_name='тема')
    description = models.TextField(max_length=250, **nullable, verbose_name='описание')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, **nullable, verbose_name='владелец')
    link_video = models.CharField(max_length=500, **nullable, verbose_name='ссылка на видео')
    material = models.TextField(**nullable, verbose_name='материал')
    file = models.FileField(upload_to='lessons/', **nullable, verbose_name='файл с уроком')
    is_published = models.BooleanField(default=False, verbose_name='признак публикации')

    def __str__(self):
        return f'Урок по теме {self.theme}: {self.title}'

    class Meta:
        verbose_name = 'урок'
        verbose_name_plural = 'уроки'
        permissions = [
            ('set_published',
             'Can publish lesson')
        ]


class Comment(models.Model):
    """Комментарий. Представляет собой вопрос по уроку/тесту,
    предложения по улучшению контента и пр.
    'theme', 'lesson','test' - взаимоисключающие поля,
    указывают, где был оставлен комментарий."""
    text = models.TextField(verbose_name='текст комментария')
    user = models.ForeignKey(User, on_delete=models.CASCADE, **nullable, verbose_name='пользователь')
    theme = models.ForeignKey(Theme, **nullable, on_delete=models.CASCADE, verbose_name='тема')
    lesson = models.ForeignKey(Lesson, **nullable, on_delete=models.CASCADE, verbose_name='урок')
    # test = models.ForeignKey(TestPaper, **nullable, on_delete=models.CASCADE, verbose_name='тест')
    date = models.DateTimeField(**nullable, verbose_name='дата и время')

    def __str__(self):
        if self.lesson:
            key_word = 'уроку'
            key_object = self.lesson
        elif self.theme:
            key_word = 'теме'
            key_object = self.theme
        else:
            key_word = 'тесту'
            key_object = 'test'
        return f'Комментарий {self.user} к {key_word} {key_object}'

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

