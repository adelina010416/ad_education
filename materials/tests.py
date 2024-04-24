from django.test import TestCase

from comments.models import Comment
from materials.models import Subject, Theme, Lesson, TestPaper
from users.models import User


class SubjectTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            email='test@mail.ru', is_active=True)
        self.super_user = User.objects.create(
            email='super_user@mail.ru', is_active=True,
            is_superuser=True, is_staff=True
        )
        self.user.set_password('test_password')
        self.super_user.set_password('su_password')
        self.user.save()
        self.super_user.save()
        self.client.force_login(user=self.user)
        self.subject = Subject.objects.create(
            name='test_subject')

    def test_subject_create(self):
        data = {'name': 'test_subject2'}
        response = self.client.post('/subjects/create/', data=data)
        self.assertEqual(response.status_code, 403)

        self.client.force_login(user=self.super_user)
        response = self.client.post('/subjects/create/', data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/subjects/')
        self.assertEqual(Subject.objects.count(), 2)

    def test_subject_list(self):
        response = self.client.get('/subjects/')
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context_data.get('object_list'),
                                 Subject.objects.all())

    def test_subject_detail(self):
        response = self.client.get(f'/subjects/{self.subject.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data.get('object'),
                         Subject.objects.get(pk=self.subject.pk))

    def test_subject_update(self):
        data = {'name': 'updated_test_subject',
                'description': 'new_description'}
        response = self.client.post(f'/subjects/update/{self.subject.pk}',
                                    data=data)
        self.assertEqual(response.status_code, 403)

        self.client.force_login(user=self.super_user)
        response = self.client.post(f'/subjects/update/{self.subject.pk}',
                                    data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/subjects/')
        self.assertEqual(
            Subject.objects.get(pk=self.subject.pk).name,
            'updated_test_subject')

    def test_subject_delete(self):
        response = self.client.post(f'/subjects/delete/{self.subject.pk}')
        self.assertEqual(response.status_code, 403)

        self.client.force_login(user=self.super_user)
        response = self.client.post(f'/subjects/delete/{self.subject.pk}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/subjects/')
        self.assertEqual(Subject.objects.count(), 0)


class ThemeTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            email='test@mail.ru', is_active=True)
        self.super_user = User.objects.create(
            email='super_user@mail.ru', is_active=True,
            is_superuser=True, is_staff=True
        )
        self.user.set_password('test_password')
        self.super_user.set_password('su_password')
        self.user.save()
        self.super_user.save()
        self.client.force_login(user=self.user)
        self.subject = Subject.objects.create(
            name='test_subject')
        self.theme = Theme.objects.create(
            title='test_theme',
            subject=self.subject,
            owner=self.user,
            is_published=True)
        self.another_theme = Theme.objects.create(
            title='another_test_theme',
            subject=self.subject,
            owner=self.super_user,
            is_published=True)
        self.lesson = Lesson.objects.create(
            title='test_lesson',
            theme=self.theme,
            owner=self.user,
            material='test_material',
            is_published=True)
        self.another_lesson = Lesson.objects.create(
            title='another_test_lesson',
            theme=self.theme,
            owner=self.super_user,
            material='test_material',
            is_published=True)
        self.test = TestPaper.objects.create(
            title='test_test',
            theme=self.theme,
            owner=self.user,
            is_published=True)
        self.another_test = TestPaper.objects.create(
            title='another_test_test',
            theme=self.theme,
            owner=self.super_user,
            is_published=True)

    def test_theme_create(self):
        data = {'title': 'test_subject2',
                'subject': self.subject.pk}
        response = self.client.post('/themes/create/', data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/my-themes/')
        self.assertEqual(Theme.objects.count(), 3)

    def test_theme_list(self):
        response = self.client.get('/my-themes/')
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context_data.get('object_list'),
                                 Theme.objects.filter(owner=self.user))

    def test_theme_detail(self):
        response = self.client.get(f'/themes/{self.theme.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data.get('object'),
                         Theme.objects.get(pk=self.theme.pk))

    def test_theme_update(self):
        data = {'title': 'updated_test_theme',
                'subject': self.subject.pk}
        response = self.client.post(f'/themes/update/{self.theme.pk}',
                                    data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/my-themes/')
        self.assertEqual(
            Theme.objects.get(pk=self.theme.pk).title,
            'updated_test_theme')
        self.assertEqual(
            Theme.objects.get(pk=self.theme.pk).is_published,
            False)

    def test_theme_delete(self):
        response = self.client.post(f'/themes/delete/{self.another_theme.pk}')
        self.assertEqual(response.status_code, 403)

        response = self.client.post(f'/themes/delete/{self.theme.pk}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/my-themes/')
        self.assertEqual(Theme.objects.count(), 1)

    def test_lesson_create(self):
        data = {'title': 'test_lesson2',
                'theme': self.theme.pk}
        response = self.client.post('/lessons/create/', data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/my-lessons/')
        self.assertEqual(Lesson.objects.count(), 3)

    def test_lesson_list(self):
        response = self.client.get('/my-lessons/')
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context_data.get('object_list'),
                                 Lesson.objects.filter(owner=self.user))

    def test_lesson_detail(self):
        data = {'text': 'Hello world'}
        response = self.client.get(f'/lessons/{self.lesson.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data.get('lesson'),
                         Lesson.objects.get(pk=self.lesson.pk))
        response = self.client.post(f'/lessons/{self.lesson.pk}', data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/lessons/{self.lesson.pk}')
        self.assertEqual(Comment.objects.count(), 1)

    def test_lesson_update(self):
        data = {'title': 'updated_test_lesson',
                'theme': self.theme.pk}
        response = self.client.post(f'/lessons/update/{self.lesson.pk}',
                                    data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/my-lessons/')
        self.assertEqual(
            Lesson.objects.get(pk=self.lesson.pk).title,
            'updated_test_lesson')
        self.assertEqual(
            Lesson.objects.get(pk=self.lesson.pk).is_published,
            False)

    def test_lesson_delete(self):
        response = self.client.post(f'/lessons/delete/'
                                    f'{self.another_lesson.pk}')
        self.assertEqual(response.status_code, 403)

        response = self.client.post(f'/lessons/delete/{self.lesson.pk}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/my-lessons/')
        self.assertEqual(Lesson.objects.count(), 1)

    def test_test_create(self):
        data = {'title': 'test_test2',
                'theme': self.theme.pk}
        response = self.client.post('/test/create/', data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'/questions/create/{TestPaper.objects.all().last().pk}')
        self.assertEqual(TestPaper.objects.count(), 3)

    def test_my_test_list(self):
        response = self.client.get('/my-tests/')
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context_data.get('object_list'),
                                 TestPaper.objects.filter(owner=self.user))

    def test_test_list(self):
        response = self.client.get(f'/test/list/{self.theme.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data.get('object_list')), 2)

    def test_test_detail(self):
        response = self.client.get(f'/test/{self.test.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data.get('object'),
                         TestPaper.objects.get(pk=self.test.pk))

    def test_test_update(self):
        data = {'title': 'updated_test_test',
                'theme': self.theme.pk}
        response = self.client.post(f'/test/update/{self.test.pk}',
                                    data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/my-tests/')
        self.assertEqual(
            TestPaper.objects.get(pk=self.test.pk).title,
            'updated_test_test')
        self.assertEqual(
            TestPaper.objects.get(pk=self.test.pk).is_published,
            False)
        response = self.client.post(f'/test/update/{self.another_test.pk}',
                                    data=data)
        self.assertEqual(response.status_code, 403)

    def test_test_delete(self):
        response = self.client.post(f'/test/delete/{self.another_test.pk}')
        self.assertEqual(response.status_code, 403)

        response = self.client.post(f'/test/delete/{self.test.pk}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/my-tests/')
        self.assertEqual(TestPaper.objects.count(), 1)
