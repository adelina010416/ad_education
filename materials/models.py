from django.db import models

from constants import nullable
from users.models import User


class Subject(models.Model):
    """Предмет"""
    name = models.CharField(
        max_length=50, unique=True, verbose_name='название')
    description = models.TextField(
        max_length=250, **nullable, verbose_name='описание')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'предмет'
        verbose_name_plural = 'предметы'


class Theme(models.Model):
    """Тема урока"""
    title = models.CharField(max_length=250, verbose_name='название')
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, verbose_name='предмет')
    description = models.TextField(
        max_length=250, **nullable, verbose_name='описание')
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, **nullable, verbose_name='владелец')
    is_published = models.BooleanField(
        default=False, verbose_name='признак публикации')

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
    theme = models.ForeignKey(
        Theme, on_delete=models.CASCADE, verbose_name='тема')
    description = models.TextField(
        max_length=250, **nullable, verbose_name='описание')
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, **nullable,
        verbose_name='владелец')
    link_video = models.CharField(
        max_length=500, **nullable, verbose_name='ссылка на видео')
    material = models.TextField(**nullable, verbose_name='материал')
    file = models.FileField(
        upload_to='lessons/', **nullable, verbose_name='файл с уроком')
    is_published = models.BooleanField(
        default=False, verbose_name='признак публикации')

    def __str__(self):
        return f'Урок по теме {self.theme}: {self.title}'

    class Meta:
        verbose_name = 'урок'
        verbose_name_plural = 'уроки'
        permissions = [
            ('set_published',
             'Can publish lesson')
        ]


class TestPaper(models.Model):
    """Тест"""
    title = models.CharField(max_length=100, verbose_name='название')
    theme = models.ForeignKey(
        Theme, on_delete=models.CASCADE, verbose_name='тема')
    description = models.TextField(**nullable, verbose_name='описание')
    owner = models.ForeignKey(
        User, **nullable, on_delete=models.CASCADE,
        verbose_name='владелец')
    is_published = models.BooleanField(
        default=False, verbose_name='признак публикации')

    def __str__(self):
        return f'Тест "{self.title}"'

    class Meta:
        verbose_name = 'тест'
        verbose_name_plural = 'тесты'


class Question(models.Model):
    """Вопрос в тесте"""
    question_text = models.TextField(verbose_name='вопрос')
    test = models.ForeignKey(
        TestPaper, **nullable, on_delete=models.CASCADE,
        verbose_name='тест')

    def __str__(self):
        return f'Вопрос "{self.question_text}"'

    class Meta:
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'


class Answer(models.Model):
    """Варианты ответов в тесте"""
    answer_text = models.CharField(max_length=300, verbose_name='ответ')
    is_correct = models.BooleanField(verbose_name='верный')
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, verbose_name='вопрос')

    def __str__(self):
        return f'Ответ "{self.answer_text}"'

    class Meta:
        verbose_name = 'ответ'
        verbose_name_plural = 'ответы'


class Result(models.Model):
    """Результат пройденного теста"""
    test = models.ForeignKey(
        TestPaper, on_delete=models.CASCADE, verbose_name='тест')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='пользователь')
    percentage = models.PositiveIntegerField(
        verbose_name='результат в процентах')
    date = models.DateTimeField(
        **nullable, verbose_name='дата и время прохождения')

    def __str__(self):
        return f'Результат теста "{self.test}"'

    class Meta:
        verbose_name = 'результат'
        verbose_name_plural = 'результаты'
