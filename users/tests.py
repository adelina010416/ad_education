from django.test import TestCase
from users.models import User


class HabitTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            email='test@mail.ru', is_active=True)
        self.user.set_password('test_password')
        self.user.save()
        self.client.force_login(user=self.user)

    def test_user_create(self):
        data = {'email': 'test_user1223@mail.ru',
                'password1': 'fysq[eqdhjnntcnsnbkznmtfnm',
                'password2': 'fysq[eqdhjnntcnsnbkznmtfnm'}
        response = self.client.post('/users/register/', data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.count(), 2)

    def test_user_detail(self):
        response = self.client.get('/users/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data.get('object'),
                         User.objects.get(pk=self.user.pk))

    def test_user_edit(self):
        data = {'phone': '9283748394',
                'city': 'Челябинск'}
        response = self.client.post('/users/profile_edit/', data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/users/profile/')
        self.assertEqual(User.objects.get(pk=self.user.pk).city,
                         'Челябинск')

    def test_user_rest_password(self):
        response = self.client.post(
            '/users/recover-password/',
            data={'email': self.user.email})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/users/reset_done/')

    def test_user_password_reset_done(self):
        response = self.client.get('/users/reset_done/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data.get('title'),
                         'Письмо с инструкциями по восстановлению '
                         'пароля отправлено')

    def test_user_password_change(self):
        data = {'old_password': 'test_password',
                'new_password1': 'skdfjhlskdjfhlkjdhfkjhks',
                'new_password2': 'skdfjhlskdjfhlkjdhfkjhks'}
        response = self.client.post('/users/password/',
                                    data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/users/password_changed/')

    def test_login_fail(self):
        response = self.client.get('/users/login-fail/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('title'),
                         'Действие недоступно')

    def test_wrong_mail(self):
        response = self.client.get('/users/wrong-mail/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('title'),
                         'Пользователь с указанной почтой не найден')

    def test_password_changed(self):
        response = self.client.get('/users/password_changed/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('title'),
                         'Пароль успешно изменён')

    def test_confirm_mail(self):
        response = self.client.get('/users/confirm-mail/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('title'),
                         'Пожалуйста, подтвердите почту.')
