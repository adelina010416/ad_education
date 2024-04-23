from django import forms
from django.forms import Textarea

from materials.forms import StyleFormMixin
from testing.models import TestPaper, Question, Answer


class TestPaperForm(forms.ModelForm, StyleFormMixin):
    class Meta:
        model = TestPaper
        exclude = ('owner', 'is_published',)
        widgets = {
            "description": Textarea(attrs={"cols": 60, "rows": 5}),
        }


class QuestionForm(forms.ModelForm, StyleFormMixin):
    class Meta:
        model = Question
        fields = ('question_text',)
        widgets = {
            "question_text": Textarea(attrs={"cols": 60, "rows": 5}),
        }


class AnswerForm(forms.ModelForm, StyleFormMixin):
    class Meta:
        model = Answer
        fields = ('answer_text', 'is_correct',)
