from django.db import models

from constants import nullable
from materials.models import Theme, Lesson, TestPaper
from users.models import User


class Comment(models.Model):
    """Комментарий. Представляет собой вопрос по уроку/тесту,
    предложения по улучшению контента и пр.
    'theme', 'lesson','test' - взаимоисключающие поля,
    указывают, где был оставлен комментарий."""
    text = models.TextField(verbose_name='текст комментария')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, **nullable,
        verbose_name='пользователь')
    theme = models.ForeignKey(
        Theme, **nullable, on_delete=models.CASCADE, verbose_name='тема')
    lesson = models.ForeignKey(
        Lesson, **nullable, on_delete=models.CASCADE,
        verbose_name='урок')
    test = models.ForeignKey(
        TestPaper, **nullable, on_delete=models.CASCADE,
        verbose_name='тест')
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
