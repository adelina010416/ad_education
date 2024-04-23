import secrets
import string

from django.core.mail import send_mail

from config import settings


def get_password():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(8))
    return password


def greeting_mail(verified_password, email):
    send_mail(
        subject='Поздравляем с регистрацией!',
        message=f'Чтобы завершить регистрацию, '
                f'перейдите по ссылке: http://127.0.0.1:8000/users/verifying?code={verified_password}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email]
    )
