import os
from datetime import datetime

import docx
import pytz
from django.contrib.auth.mixins import LoginRequiredMixin, \
    PermissionRequiredMixin, UserPassesTestMixin
from django.core import exceptions
from django.forms import inlineformset_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView, \
    DeleteView, UpdateView, TemplateView

from comments.forms import CommentForm
from comments.models import Comment
from config.settings import MEDIA_ROOT, TIME_ZONE
from materials.forms import SubjectForm, ThemeForm, LessonForm, \
    TestPaperForm, QuestionForm, AnswerForm
from materials.models import Subject, Theme, Lesson, Question, Answer, \
    Result, TestPaper
from materials.services import check_published, create_result, \
    get_user_answer_dict


def home(request):
    """Домашняя страница"""
    context = {'lessons': Lesson.objects.all().count(),
               'themes': Theme.objects.all().count(),
               'subjects': Subject.objects.all()[:5],
               'subjects_count': Subject.objects.all().count(),
               'tests_count': TestPaper.objects.all().count()}
    return render(request, 'materials/home.html', context)


# SUBJECT VIEWS ########################################################

class SubjectCreateView(LoginRequiredMixin, PermissionRequiredMixin,
                        CreateView):
    """
    Создаёт экземпляр класса Subject.
    Доступно только персонала.
    """
    model = Subject
    form_class = SubjectForm
    permission_required = "materials.add_subject"
    success_url = reverse_lazy('material:subjects')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Предмет'
        return context


class SubjectListView(ListView):
    """
    Возвращает список предметов.
    Для персонала есть ссылка на добавление предмета
    """
    model = Subject


class SubjectDetailView(LoginRequiredMixin, DetailView):
    """
    Возвращает страницу с подробностями по определённому
    предмету и список тем по этому предмету (только опубликованные темы
    - для обычного юзера, все темы со ссылками на
    редактирование и удаление предмета
    и публикацию/снятие с публикации тем - для персонала)
    """
    model = Subject

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_staff:
            context['theme_set'] = Theme.objects.filter(subject=self.object)
        else:
            context['theme_set'] = Theme.objects.filter(
                subject=self.object, is_published=True)
        return context


class SubjectUpdateView(LoginRequiredMixin, PermissionRequiredMixin,
                        UpdateView):
    """
    Редактирование предмета
    (доступно только персоналу)
    """
    model = Subject
    form_class = SubjectForm
    permission_required = "materials.change_subject"
    success_url = reverse_lazy('material:subjects')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Предмет'
        return context


class SubjectDeleteView(LoginRequiredMixin,
                        PermissionRequiredMixin, DeleteView):
    """
    Удаление предмета
    (доступно только персоналу)
    """
    model = Subject
    permission_required = "materials.delete_subject"
    success_url = reverse_lazy('material:subjects')
    template_name = 'materials/confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['text'] = f'Хотите удалить предмет "{self.object.name}" ' \
                          f'и все материалы, связанные с ним?'
        context['cancel_url'] = 'material:subjects'
        return context


# ### THEME VIEWS #######################################################

class ThemeCreateView(LoginRequiredMixin, CreateView):
    """
    Создание темы
    """
    model = Theme
    form_class = ThemeForm
    template_name = 'materials/subject_form.html'
    success_url = reverse_lazy('material:my_themes')

    def form_valid(self, form):
        if form.is_valid():
            theme = form.save()
            theme.owner = self.request.user
            theme.is_published = False
            theme.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Тема'
        return context


def set_published_theme(request, pk):
    """
    В зависимости от текущего статуса темы
    публикует или снимает с публикации тему
    (доступно только персоналу)
    """
    if request.user.is_staff:
        theme = get_object_or_404(Theme, pk=pk)
        if theme.is_published:
            theme.is_published = False
        else:
            theme.is_published = True
        theme.save()
        return redirect('material:subject_detail', theme.subject.id)
    raise exceptions.PermissionDenied


class MyThemeListView(LoginRequiredMixin, ListView):
    """
    Список тем, созданных текущим пользователем
    """
    model = Theme

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = Theme.objects.filter(owner=self.request.user)
        return context


class ThemeDetailView(LoginRequiredMixin, DetailView):
    """
    Возвращает заголовок и описание темы,
    а также список всех уроков по этой теме
    (только опубликованных - для обычного пользователя,
    всех - для персонала)
    и ссылки на тесты и комментарии по теме
    """
    model = Theme

    def get_object(self, *args, **kwargs):
        obj = super().get_object(**kwargs)
        return check_published(obj, self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_staff:
            context['lesson_set'] = Lesson.objects.filter(theme=self.object)
        else:
            context['lesson_set'] = Lesson.objects.filter(
                theme=self.object, is_published=True)
        return context


class ThemeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Редактирование темы
    (доступно только владельцу темы)
    """
    model = Theme
    form_class = ThemeForm
    template_name = 'materials/subject_form.html'
    success_url = reverse_lazy('material:my_themes')

    def test_func(self):
        is_owner = Theme.objects.filter(
            pk=self.kwargs['pk']).last().owner == self.request.user
        return is_owner

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Тема'
        return context

    def form_valid(self, form):
        if form.is_valid():
            theme = form.save()
            theme.is_published = False
            theme.save()
        return super().form_valid(form)


class ThemeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Удаление темы
    (доступно только владельцу темы)
    """
    model = Theme
    success_url = reverse_lazy('material:my_themes')
    template_name = 'materials/confirm_delete.html'

    def test_func(self):
        is_owner = Theme.objects.filter(
            pk=self.kwargs['pk']).last().owner == self.request.user
        return is_owner

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['text'] = f'Хотите удалить тему "{self.object.title}" ' \
                          f'и все уроки, связанные с ней?'
        context['cancel_url'] = 'material:my_themes'
        return context


# LESSON VIEWS #########################################################

def set_published_lesson(request, pk):
    """
    В зависимости от текущего статуса урока
    публикует или снимает с публикации его
    (доступно только персоналу)
    """
    if request.user.is_staff:
        lesson = get_object_or_404(Lesson, pk=pk)
        if lesson.is_published:
            lesson.is_published = False
        else:
            lesson.is_published = True
        lesson.save()
        return redirect('material:theme_detail', lesson.theme.id)
    raise exceptions.PermissionDenied


class LessonCreateView(LoginRequiredMixin, CreateView):
    """Создание Урока"""
    model = Lesson
    form_class = LessonForm
    template_name = 'materials/subject_form.html'
    success_url = reverse_lazy('material:my_lessons')

    def form_valid(self, form):
        if form.is_valid():
            lesson = form.save()
            lesson.owner = self.request.user
            lesson.is_published = False
            lesson.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Урок'
        return context


class MyLessonListView(LoginRequiredMixin, ListView):
    """
    Возвращает список уроков, созданных пользователем
    """
    model = Lesson

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = Lesson.objects.filter(owner=self.request.user)
        return context


class LessonDetailView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Отображает материал урока, все комментарии по нему,
    форму для создания комментария по уроку
    """
    model = Comment
    form_class = CommentForm
    template_name = 'materials/lesson_detail.html'

    def test_func(self):
        if self.request.user == get_object_or_404(
                Lesson, pk=self.kwargs['pk']).owner\
                or self.request.user.is_staff:
            return True
        else:
            return get_object_or_404(Lesson, pk=self.kwargs['pk']).is_published

    def get_object(self, *args, **kwargs):
        obj = super().get_object(**kwargs)
        if self.request.user == obj.owner:
            return obj
        else:
            return check_published(obj, self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = get_object_or_404(Lesson, pk=self.kwargs['pk'])
        if lesson.file:
            path = os.path.join(MEDIA_ROOT, str(lesson.file))
            doc = docx.Document(path)
            text = []
            [text.append(paragraph.text) for paragraph in doc.paragraphs]
            context['file'] = text
        context['object_list'] = Comment.objects.filter(lesson=lesson)
        context['lesson'] = lesson
        if lesson.link_video:
            video_str = lesson.link_video.split("/")[3]
            if video_str.startswith('watch'):
                video_id = video_str.split('=')[1]
            else:
                video_id = video_str.split('?')[0]
            context['video_player'] = f'https://www.youtube.com/embed/' \
                                      f'{video_id}?rel=0'
        return context

    def form_valid(self, form):
        if form.is_valid():
            comment = form.save()
            comment.user = self.request.user
            comment.lesson = Lesson.objects.filter(
                pk=self.kwargs['pk']).first()
            comment.date = datetime.now(pytz.timezone(TIME_ZONE))
            comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('material:lesson_detail', args=[self.kwargs.get('pk')])


class LessonUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Редактирование урока
    (доступно только владельцу)
    """
    model = Lesson
    form_class = LessonForm
    template_name = 'materials/subject_form.html'
    success_url = reverse_lazy('material:my_lessons')

    def test_func(self):
        is_owner = Lesson.objects.filter(
            pk=self.kwargs['pk']).last().owner == self.request.user
        return is_owner

    def form_valid(self, form):
        if form.is_valid():
            lesson = form.save()
            lesson.owner = self.request.user
            lesson.is_published = False
            lesson.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Урок'
        return context


class LessonDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Удаление урока
    (доступно только владельцу)
    """
    model = Lesson
    success_url = reverse_lazy('material:my_lessons')
    template_name = 'materials/confirm_delete.html'

    def test_func(self):
        is_owner = Lesson.objects.filter(
            pk=self.kwargs['pk']).last().owner == self.request.user
        return is_owner

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['text'] = f'Хотите удалить урок "{self.object.title}"?'
        context['cancel_url'] = 'material:my_lessons'
        return context


# TEST VIEWS ###########################################################

class TestingCreateView(LoginRequiredMixin, CreateView):
    """
    Создание теста (заголовок, тема и описание)
    """
    model = TestPaper
    form_class = TestPaperForm
    template_name = 'testing/testpaper_form.html'

    def form_valid(self, form):
        if form.is_valid():
            test = form.save()
            test.owner = self.request.user
            test.is_published = False
            test.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('material:question_create', args=[self.object.id])


class MyTestsView(LoginRequiredMixin, ListView):
    """Список тестов, созданных пользователем"""
    model = TestPaper
    template_name = 'testing/my_test_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = TestPaper.objects.filter(
            owner=self.request.user)
        return context


class TestListView(LoginRequiredMixin, ListView):
    """
    Возвращает заголовок и описание темы,
    а также список всех тестов по этой теме
    (только опубликованных - для обычного пользователя,
    всех - для персонала)
    и ссылки на тесты и комментарии по теме
    """
    model = TestPaper
    template_name = 'testing/testpaper_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['theme'] = Theme.objects.filter(pk=self.kwargs['pk']).first()
        if self.request.user.is_staff:
            context['object_list'] = TestPaper.objects.filter(
                theme=context['theme'])
        else:
            context['object_list'] = TestPaper.objects.filter(
                theme=context['theme'], is_published=True)
        return context


class TestDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Возвращает заголовок и описание темы,
    а также список всех уроков по этой теме
    (только опубликованных - для обычного пользователя,
    всех - для персонала)
    и ссылки на тесты и комментарии по теме
    """
    model = TestPaper
    template_name = 'testing/testpaper_detail.html'

    def test_func(self):
        if self.request.user == get_object_or_404(
                TestPaper, pk=self.kwargs['pk']).owner\
                or self.request.user.is_staff:
            return True
        else:
            return get_object_or_404(
                TestPaper, pk=self.kwargs['pk']).is_published

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_owner'] = self.object.owner == self.request.user
        return context


class TestUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Редактирование теста
    (доступно только владельцу)
    """
    model = TestPaper
    form_class = TestPaperForm
    success_url = reverse_lazy('material:my_tests')
    template_name = 'testing/testpaper_form.html'

    def test_func(self):
        is_owner = TestPaper.objects.filter(
            pk=self.kwargs['pk']).last().owner == self.request.user
        return is_owner

    def form_valid(self, form):
        if form.is_valid():
            test = form.save()
            test.owner = self.request.user
            test.is_published = False
            test.save()
        return super().form_valid(form)


class TestDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Удаление теста
    (доступно только владельцу)
    """
    model = TestPaper
    success_url = reverse_lazy('material:my_tests')
    template_name = 'testing/testpaper_confirm_delete.html'

    def test_func(self):
        is_owner = TestPaper.objects.filter(
            pk=self.kwargs['pk']).last().owner == self.request.user
        return is_owner

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['text'] = f'Хотите удалить тест "{self.object.title}"?'
        context['cancel_url'] = 'material:my_tests'
        return context


def set_published_test(request, pk):
    """
    В зависимости от текущего статуса темы
    публикует или снимает с публикации тест
    (доступно только персоналу)
    """
    if request.user.is_staff:
        test = get_object_or_404(TestPaper, pk=pk)
        if test.is_published:
            test.is_published = False
        else:
            test.is_published = True
        test.save()
        return redirect('material:test_list', test.theme.id)
    raise exceptions.PermissionDenied


# QUESTION VIEWS ########################################################

class QuestionCreateView(LoginRequiredMixin, CreateView):
    """Создание вопроса и ответов к нему"""
    model = Question
    form_class = QuestionForm
    template_name = 'testing/question_form.html'

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['test_pk'] = self.kwargs['pk']

        AnswerFormset = inlineformset_factory(
            Question, Answer, form=AnswerForm, extra=4
        )
        if self.request.method == 'POST':
            context_data['formset'] = AnswerFormset(
                self.request.POST, instance=self.object)
        else:
            context_data['formset'] = AnswerFormset(instance=self.object)
        return context_data

    def form_valid(self, form):
        formset = self.get_context_data()['formset']
        if form.is_valid():
            question = form.save()
            question.test = TestPaper.objects.get(pk=self.kwargs.get('pk'))
            question.save()
            if formset.is_valid():
                formset.instance = question
                formset.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('material:question_create', args=[self.kwargs['pk']])


class QuestionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Редактирование вопроса и ответов
    (доступно только владельцу)
    """
    model = Question
    form_class = QuestionForm
    template_name = 'testing/question_form.html'

    def test_func(self):
        is_owner = Question.objects.filter(
            pk=self.kwargs['pk']
        ).last().test.owner == self.request.user
        return is_owner

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['test_pk'] = self.kwargs['pk']

        AnswerFormset = inlineformset_factory(
            Question, Answer, form=AnswerForm, extra=4
        )
        if self.request.method == 'POST':
            context_data['formset'] = AnswerFormset(
                self.request.POST, instance=self.object)
        else:
            context_data['formset'] = AnswerFormset(instance=self.object)
        return context_data

    def form_valid(self, form):
        formset = self.get_context_data()['formset']
        if form.is_valid():
            question = form.save()
            question.save()
            if formset.is_valid():
                formset.instance = question
                formset.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('material:test_detail', args=[self.object.test.id])


class QuestionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Удаление вопроса
    """
    model = Question
    template_name = 'testing/question_confirm_delete.html'

    def test_func(self):
        is_owner = Question.objects.filter(
            pk=self.kwargs['pk']
        ).last().test.owner == self.request.user
        return is_owner

    def get_success_url(self):
        return reverse('material:test_detail', args=[self.object.test.id])


#  TEST PASSING VIEWS ####################################################

class TestPassView(LoginRequiredMixin, DetailView):
    """
    Страница прохождения теста
    """
    model = TestPaper
    template_name = 'testing/test_passing.html'


class ResultCreateView(LoginRequiredMixin, TemplateView):
    """
    Возвращает страницу с результатами по пройденному тесту
    и создаёт экземпляр класса Result
    """
    template_name = 'testing/result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        test = get_object_or_404(TestPaper, pk=self.kwargs['pk'])
        user_answers = self.request.GET
        context['result'] = create_result(
            test, user_answers, self.request.user)
        context['answers'] = get_user_answer_dict(test, user_answers)
        context['test'] = test
        return context


#  TEST RESULTS VIEWS ###################################################

class ResultListView(LoginRequiredMixin, ListView):
    """
    Возвращает список всех результатов пользователя
    """
    model = Result
    template_name = 'testing/result_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = Result.objects.filter(user=self.request.user)
        return context


class ResultDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Удаление результата
    (доступно только владельцу)
    """
    model = Result
    success_url = reverse_lazy('material:my_result')
    template_name = 'testing/result_confirm_delete.html'

    def test_func(self):
        return Result.objects.filter(
            pk=self.kwargs['pk']
        ).last().user == self.request.user
