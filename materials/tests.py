from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Subject, Theme, Lesson
from users.models import User


class HabitsAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            email='test@mail.ru', is_active=True)
        self.user.set_password('test_password')
        self.user.save()
        self.client.force_authenticate(user=self.user)
        self.subject = Subject.objects.create(
            name='test_subject')
        self.theme = Theme.objects.create(
            title='test_theme',
            subject=self.subject,
            owner=self.user,
            is_published=True)
        self.lesson = Lesson.objects.create(
            title='test_lesson',
            theme=self.theme,
            owner=self.user,
            material='test_material',
            is_published=True)

    def test_subject_list(self):
        """ Проверка списка публичных привычек """
        response = self.client.get('/subjects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

