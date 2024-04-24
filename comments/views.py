from datetime import datetime

import pytz
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DeleteView

from comments.filters import CommentFilter
from comments.forms import CommentForm
from comments.models import Comment
from config.settings import TIME_ZONE
from materials.models import Theme, TestPaper


class ThemeCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'comments/comment_theme.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = Comment.objects.filter(
            theme=self.kwargs['pk'])
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
        return reverse('comments:theme_comments', args=[self.kwargs.get('pk')])


class TestCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'comments/comment_test.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = Comment.objects.filter(test=self.kwargs['pk'])
        context['test'] = TestPaper.objects.filter(
            pk=self.kwargs['pk']).first()
        return context

    def form_valid(self, form):
        if form.is_valid():
            comment = form.save()
            comment.user = self.request.user
            comment.test = TestPaper.objects.filter(
                pk=self.kwargs['pk']).first()
            comment.date = datetime.now(pytz.timezone(TIME_ZONE))
            comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('comments:test_comments', args=[self.kwargs.get('pk')])


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    success_url = reverse_lazy('comments:my_comments')

    def test_func(self):
        is_owner = Comment.objects.filter(
            pk=self.kwargs['pk']).last().user == self.request.user
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
        elif search_object == 'test__title':
            context['search_help'] = 'Поиск_по_названию_теста'
        else:
            context['search_help'] = 'Сначала_выберите_способ_поиска'
        context['search_object'] = search_object
        qs = Comment.objects.filter(user=self.request.user)
        filtered_comments = CommentFilter(self.request.GET, queryset=qs).qs
        context['object_list'] = filtered_comments
        return context


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    success_url = reverse_lazy('comments:my_comments')
    template_name = 'materials/confirm_delete.html'

    def test_func(self):
        is_owner = Comment.objects.filter(
            pk=self.kwargs['pk']).last().user == self.request.user
        return is_owner

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.theme:
            key_phrase = f'теме "{self.object.theme.title}"'
        elif self.object.test:
            key_phrase = f'тесту "{self.object.test.title}"'
        else:
            key_phrase = f'уроку "{self.object.lesson.title}"'
        context['text'] = f'Хотите удалить ваш комментарий к {key_phrase}?'
        context['cancel_url'] = 'comments:my_comments'
        return context
