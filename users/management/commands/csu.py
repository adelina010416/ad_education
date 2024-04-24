from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.create(
            email='super_user@mail.ru',
            first_name='Ivan',
            last_name='Ivanov',
            is_staff=True,
            is_superuser=True
        )
        user.set_password('password')
        user.save()
