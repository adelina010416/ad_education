from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordChangeView
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DetailView, UpdateView, ListView

from config import settings
from users.forms import UserRegisterForm, UserProfileForm
from users.models import User
from users.services import get_password, greeting_mail


def verify_view(request):
    """Сообщает об успешном подтверждении почты"""
    code = request.GET.get('code')
    user = User.objects.get(verified_password=code)
    user.is_active = True
    user.save()
    context = {'title': 'Добро пожаловать!',
               'text': 'Почта успешно подтверждена'}
    return render(request, 'users/information.html', context)


def confirm_mail(request):
    """Запрос на подтверждение почты после регистрации на сайте"""
    context = {'title': 'Пожалуйста, подтвердите почту.',
               'text': 'Для окончания регистрации Вам нужно пройти по ссылке в письме, '
                       'которое было отправлено Вам на указанный e-mail.'}
    return render(request, 'users/information.html', context)


def password_changed(request):
    """Подтверждает успешную смену пароля"""
    context = {'title': 'Пароль успешно изменён'}
    return render(request, 'users/information.html', context)


def wrong_mail(request):
    """Сообщение о неверно введённом адресе почты при восстановлении пароля"""
    context = {'title': 'Пользователь с указанной почтой не найден',
               'text': 'Пожалуйста, проверьте корректность введённой почты, либо зарегистрируйтесь, '
                       'используя указанную почту.'}
    return render(request, 'users/information.html', context)


def login_fail(request):
    context = {'title': 'Действие недоступно',
               'text': 'Чтобы пользоваться всеми возможностями сервиса, '
                       'пожалуйста, войдите в свою учётную запись или зарегистрируйтесь.'}
    return render(request, 'users/information.html', context)


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Регистрация', 'button': 'Сохранить'}
    success_url = reverse_lazy('users:confirm_mail')

    def form_valid(self, form):
        new_user = form.save()
        new_user.verified_password = get_password()
        new_user.is_active = False
        greeting_mail(new_user.verified_password, new_user.email)
        return super().form_valid(form)


class UserProfileView(DetailView):
    model = User
    template_name = 'users/user_profile.html'

    def get_object(self, queryset=None):
        return self.request.user


class EditProfileView(UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Редактирование профиля', 'button': 'Сохранить'}
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


class UserPasswordResetView(PasswordResetView):
    email_template_name = 'users/reset.html'
    from_email = settings.EMAIL_HOST_USER
    new_password = get_password()
    extra_email_context = {'password': new_password}

    template_name = 'users/login.html'
    extra_context = {'title': 'Сброс пароля',
                     'button': 'Отправить',
                     'text': 'Введите свой e-mail, указанный в профиле.'}
    success_url = reverse_lazy('users:reset_done')

    def form_valid(self, form):
        user_mail = form.cleaned_data.get('email')

        try:
            user = User.objects.get(email=user_mail)
            user.set_password(self.new_password)
            user.save()
            return super().form_valid(form)

        except ObjectDoesNotExist:
            return redirect(reverse('users:wrong_mail'))


class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/information.html'
    extra_context = {'title': 'Письмо с инструкциями по восстановлению пароля отправлено',
                     'text': 'Мы отправили вам письмо с новым паролем на указанный адрес'
                             ' электронной почты (если в нашей базе данных есть такой адрес). '
                             'Вы должны получить ее в ближайшее время. Если вы не получили письмо, пожалуйста, '
                             'убедитесь, что вы ввели почту, с которой Вы зарегистрировались, '
                             'и проверьте папку со спамом.'}


class UserPasswordChangeView(PasswordChangeView):
    template_name = 'users/login.html'
    extra_context = {'button': 'Сохранить'}
    success_url = reverse_lazy('users:password_changed')
