from django.db import models

from constants import nullable
from materials.models import Theme
from users.models import User


class TestPaper(models.Model):
    """Тест"""
    title = models.CharField(max_length=100, verbose_name='название')
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, verbose_name='тема')
    description = models.TextField(**nullable, verbose_name='описание')
    owner = models.ForeignKey(User, **nullable, on_delete=models.CASCADE, verbose_name='владелец')
    is_published = models.BooleanField(default=False, verbose_name='признак публикации')

    def __str__(self):
        return f'Тест "{self.title}"'

    class Meta:
        verbose_name = 'тест'
        verbose_name_plural = 'тесты'


class Question(models.Model):
    """Вопрос в тесте"""
    question_text = models.TextField(verbose_name='вопрос')
    test = models.ForeignKey(TestPaper, **nullable, on_delete=models.CASCADE, verbose_name='тест')

    def __str__(self):
        return f'Вопрос "{self.question_text}"'

    class Meta:
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'


class Answer(models.Model):
    """Варианты ответов"""
    answer_text = models.CharField(max_length=300, verbose_name='ответ')
    is_correct = models.BooleanField(verbose_name='верный')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='вопрос')

    def __str__(self):
        return f'Ответ "{self.answer_text}"'

    class Meta:
        verbose_name = 'ответ'
        verbose_name_plural = 'ответы'


class Result(models.Model):
    """Результат пройденного теста"""
    test = models.ForeignKey(TestPaper, on_delete=models.CASCADE, verbose_name='тест')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='пользователь')
    percentage = models.PositiveIntegerField(verbose_name='результат в процентах')
    date = models.DateTimeField(**nullable, verbose_name='дата и время прохождения')

    def __str__(self):
        return f'Результат теста "{self.test}"'

    class Meta:
        verbose_name = 'результат'
        verbose_name_plural = 'результаты'
