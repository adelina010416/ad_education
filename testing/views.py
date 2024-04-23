from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core import exceptions
from django.forms import inlineformset_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView, TemplateView

from materials.models import Theme
from materials.services import create_dict, get_user_answer_dict, create_result
from testing.forms import TestPaperForm, QuestionForm, AnswerForm
from testing.models import TestPaper, Question, Answer, Result


# ################################### TEST VIEWS ###########################################################

class TestingCreateView(LoginRequiredMixin, CreateView):
    model = TestPaper
    form_class = TestPaperForm

    def form_valid(self, form):
        if form.is_valid():
            test = form.save()
            test.owner = self.request.user
            test.is_published = False
            test.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('tests:question_create', args=[self.object.id])


class MyTestsView(LoginRequiredMixin, ListView):
    model = TestPaper
    template_name = 'testing/my_test_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = TestPaper.objects.filter(owner=self.request.user)
        return context


class TestListView(LoginRequiredMixin, ListView):
    model = TestPaper

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['theme'] = Theme.objects.filter(pk=self.kwargs['pk']).first()
        if self.request.user.is_staff:
            context['object_list'] = TestPaper.objects.filter(theme=context['theme'])
        else:
            context['object_list'] = TestPaper.objects.filter(theme=context['theme'], is_published=True)
        return context


class TestDetailView(LoginRequiredMixin, DetailView):
    model = TestPaper

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_owner'] = self.object.owner == self.request.user
        return context


class TestUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = TestPaper
    form_class = TestPaperForm
    success_url = reverse_lazy('tests:my_tests')

    def test_func(self):
        is_owner = TestPaper.objects.filter(pk=self.kwargs['pk']).last().owner == self.request.user
        return is_owner

    def form_valid(self, form):
        if form.is_valid():
            test = form.save()
            test.owner = self.request.user
            test.is_published = False
            test.save()
        return super().form_valid(form)


class TestDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = TestPaper
    success_url = reverse_lazy('tests:my_tests')

    def test_func(self):
        is_owner = TestPaper.objects.filter(pk=self.kwargs['pk']).last().owner == self.request.user
        return is_owner

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['text'] = f'Хотите удалить тест "{self.object.title}"?'
        context['cancel_url'] = 'tests:my_tests'
        return context


def set_published_lesson(request, pk):
    if request.user.is_staff:
        test = get_object_or_404(TestPaper, pk=pk)
        if test.is_published:
            test.is_published = False
        else:
            test.is_published = True
        test.save()
        return redirect('tests:test_list', test.theme.id)
    raise exceptions.PermissionDenied


# ################################### QUESTION VIEWS ###########################################################

class QuestionCreateView(LoginRequiredMixin, CreateView):
    model = Question
    form_class = QuestionForm

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['test_pk'] = self.kwargs['pk']

        AnswerFormset = inlineformset_factory(
            Question, Answer, form=AnswerForm, extra=4
        )
        if self.request.method == 'POST':
            context_data['formset'] = AnswerFormset(self.request.POST, instance=self.object)
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
        return reverse('tests:question_create', args=[self.kwargs['pk']])


class QuestionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Question
    form_class = QuestionForm

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
            context_data['formset'] = AnswerFormset(self.request.POST, instance=self.object)
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
        return reverse('tests:test_detail', args=[self.object.test.id])


class QuestionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Question

    def test_func(self):
        is_owner = Question.objects.filter(
            pk=self.kwargs['pk']
        ).last().test.owner == self.request.user
        return is_owner

    def get_success_url(self):
        return reverse('tests:test_detail', args=[self.object.test.id])


# ################################### TEST PASSING VIEWS ###########################################################

class TestPassView(LoginRequiredMixin, DetailView):
    model = TestPaper
    template_name = 'testing/test_passing.html'


class ResultCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'testing/result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        test = get_object_or_404(TestPaper, pk=self.kwargs['pk'])
        user_answers = self.request.GET
        context['result'] = create_result(test, user_answers, self.request.user)
        context['answers'] = get_user_answer_dict(test, user_answers)
        context['test'] = test
        return context


# ################################### TEST RESULTS VIEWS ###########################################################

class ResultListView(LoginRequiredMixin, ListView):
    model = Result

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = Result.objects.filter(user=self.request.user)
        return context


class ResultDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Result
    success_url = reverse_lazy('tests:my_result')

    def test_func(self):
        return Result.objects.filter(
            pk=self.kwargs['pk']
        ).last().user == self.request.user

