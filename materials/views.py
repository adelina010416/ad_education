import os
from datetime import datetime
from pprint import pprint

import docx
import pytz
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.core import exceptions
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView, DeleteView, UpdateView
from django_filters.rest_framework import DjangoFilterBackend

from config.settings import MEDIA_ROOT, TIME_ZONE
from materials.filters import CommentFilter, ThemeFilter
from materials.forms import SubjectForm, ThemeForm, LessonForm, CommentForm
from materials.models import Subject, Theme, Lesson, Comment
from materials.services import check_published
from testing.models import TestPaper


def home(request):
    context = {'lessons': Lesson.objects.all().count(),
               'themes': Theme.objects.all().count(),
               'subjects': Subject.objects.all()[:5],
               'subjects_count': Subject.objects.all().count(),
               'tests_count': TestPaper.objects.all().count()}
    return render(request, 'materials/home.html', context)


# _________________________________________SUBJECT VIEWS____________________________________________________

class SubjectCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Subject
    form_class = SubjectForm
    permission_required = "materials.add_subject"
    success_url = reverse_lazy('material:subjects')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Предмет'
        return context


class SubjectListView(ListView):
    model = Subject


class SubjectDetailView(LoginRequiredMixin, DetailView):
    model = Subject

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_staff:
            context['theme_set'] = Theme.objects.filter(subject=self.object)
        else:
            context['theme_set'] = Theme.objects.filter(subject=self.object, is_published=True)
        return context


class SubjectUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Subject
    form_class = SubjectForm
    permission_required = "materials.change_subject"
    success_url = reverse_lazy('material:subjects')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Предмет'
        return context


class SubjectDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
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


# ____________________________________________THEME VIEWS___________________________________________________

class ThemeCreateView(LoginRequiredMixin, CreateView):
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
    model = Theme

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = Theme.objects.filter(owner=self.request.user)
        return context


class ThemeDetailView(LoginRequiredMixin, DetailView):
    model = Theme

    def get_object(self, *args, **kwargs):
        obj = super().get_object(**kwargs)
        return check_published(obj, self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.request)
        if self.request.user.is_staff:
            context['lesson_set'] = Lesson.objects.filter(theme=self.object)
        else:
            context['lesson_set'] = Lesson.objects.filter(theme=self.object, is_published=True)
        return context


class ThemeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Theme
    form_class = ThemeForm
    template_name = 'materials/subject_form.html'
    success_url = reverse_lazy('material:my_themes')

    def test_func(self):
        is_owner = Theme.objects.filter(pk=self.kwargs['pk']).last().owner == self.request.user
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
    model = Theme
    success_url = reverse_lazy('material:my_themes')
    template_name = 'materials/confirm_delete.html'

    def test_func(self):
        is_owner = Theme.objects.filter(pk=self.kwargs['pk']).last().owner == self.request.user
        return is_owner

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['text'] = f'Хотите удалить тему "{self.object.title}" ' \
                          f'и все уроки, связанные с ней?'
        context['cancel_url'] = 'material:my_themes'
        return context


# __________________________________ LESSON VIEWS___________________________________________________________

def set_published_lesson(request, pk):
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
    model = Lesson

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = Lesson.objects.filter(owner=self.request.user)
        return context


class LessonDetailView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'materials/lesson_detail.html'

    def get_object(self, *args, **kwargs):
        obj = super().get_object(**kwargs)
        return check_published(obj, self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = get_object_or_404(Lesson, pk=self.kwargs['pk'], is_published=True)
        path = os.path.join(MEDIA_ROOT, str(lesson.file))
        doc = docx.Document(path)
        text = []
        [text.append(paragraph.text) for paragraph in doc.paragraphs]
        context['file'] = text
        context['object_list'] = Comment.objects.filter(lesson=lesson)
        context['lesson'] = lesson
        video_str = lesson.link_video.split("/")[3]
        if video_str.startswith('watch'):
            video_id = video_str.split('=')[1]
        else:
            video_id = video_str.split('?')[0]
        context['video_player'] = f'https://www.youtube.com/embed/{video_id}?rel=0'
        return context

    def form_valid(self, form):
        if form.is_valid():
            comment = form.save()
            comment.user = self.request.user
            comment.lesson = Lesson.objects.filter(pk=self.kwargs['pk']).first()
            comment.date = datetime.now(pytz.timezone(TIME_ZONE))
            comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('material:lesson_detail', args=[self.kwargs.get('pk')])


class LessonUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'materials/subject_form.html'
    success_url = reverse_lazy('material:my_lessons')

    def test_func(self):
        is_owner = Lesson.objects.filter(pk=self.kwargs['pk']).last().owner == self.request.user
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
    model = Lesson
    success_url = reverse_lazy('material:my_lessons')
    template_name = 'materials/confirm_delete.html'

    def test_func(self):
        is_owner = Lesson.objects.filter(pk=self.kwargs['pk']).last().owner == self.request.user
        return is_owner

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['text'] = f'Хотите удалить урок "{self.object.title}"?'
        context['cancel_url'] = 'material:my_lessons'
        return context


# _________________________________COMMENT VIEWS____________________________________________________

class ThemeCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'materials/comment_theme.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = Comment.objects.filter(theme=self.kwargs['pk'])
        context['theme'] = Theme.objects.filter(pk=self.kwargs['pk']).first()
        return context

    def form_valid(self, form):
        if form.is_valid():
            comment = form.save()
            comment.user = self.request.user
            comment.theme = Theme.objects.filter(pk=self.kwargs['pk']).first()
            comment.date = datetime.now(pytz.timezone(TIME_ZONE))
            comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('material:theme_comments', args=[self.kwargs.get('pk')])


class TestCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'materials/comment_theme.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = Comment.objects.filter(theme=self.kwargs['pk'])
        context['theme'] = Theme.objects.filter(pk=self.kwargs['pk']).first()
        return context

    def form_valid(self, form):
        if form.is_valid():
            comment = form.save()
            comment.user = self.request.user
            comment.theme = Theme.objects.filter(pk=self.kwargs['pk']).first()
            comment.date = datetime.now(pytz.timezone(TIME_ZONE))
            comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('material:theme_comments', args=[self.kwargs.get('pk')])


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    success_url = reverse_lazy('material:my_comments')

    def test_func(self):
        is_owner = Comment.objects.filter(pk=self.kwargs['pk']).last().user == self.request.user
        return is_owner


class MyCommentListView(LoginRequiredMixin, ListView):
    model = Comment

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        search_object = self.request.GET.get('query_object')
        if search_object == 'text':
            context['search_help'] = 'Поиск_по_тексту_комментария'
        elif search_object == 'theme__title':
            context['search_help'] = 'Поиск_по_названию_темы'
        elif search_object == 'lesson__title':
            context['search_help'] = 'Поиск_по_названию_урока'
        else:
            context['search_help'] = 'Сначала_выберите_способ_поиска'
        context['search_object'] = search_object
        qs = Comment.objects.filter(user=self.request.user)
        filtered_comments = CommentFilter(self.request.GET, queryset=qs).qs
        context['object_list'] = filtered_comments
        return context


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    success_url = reverse_lazy('material:my_comments')
    template_name = 'materials/confirm_delete.html'

    def test_func(self):
        is_owner = Comment.objects.filter(pk=self.kwargs['pk']).last().user == self.request.user
        return is_owner

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.theme:
            key_phrase = f'теме "{self.object.theme.title}"'
        else:
            key_phrase = f'уроку "{self.object.lesson.title}"'
        context['text'] = f'Хотите удалить ваш комментарий к {key_phrase}?'
        context['cancel_url'] = 'material:my_comments'
        return context
