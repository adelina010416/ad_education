from django.contrib.auth.models import AbstractUser
from django.db import models

from constants import nullable


class User(AbstractUser):
    username = None
    email = models.EmailField(max_length=250, unique=True, verbose_name='почта')
    phone = models.CharField(max_length=50, unique=True, **nullable, verbose_name='телефон')
    city = models.CharField(max_length=100, **nullable, verbose_name='город')
    avatar = models.ImageField(upload_to='users/', **nullable, verbose_name='аватар')
    verified_password = models.CharField(verbose_name='ключ для верификации', **nullable)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
