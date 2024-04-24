from django import forms
from django.forms import Textarea

from materials.models import Subject, Theme, Lesson, TestPaper, \
    Question, Answer


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class SubjectForm(forms.ModelForm, StyleFormMixin):
    """Форма для модели Subject"""

    class Meta:
        model = Subject
        fields = '__all__'


class ThemeForm(forms.ModelForm, StyleFormMixin):
    """Форма для модели Theme"""

    class Meta:
        model = Theme
        exclude = ('owner', 'is_published',)


class LessonForm(forms.ModelForm, StyleFormMixin):
    """Форма для модели Lesson"""

    class Meta:
        model = Lesson
        exclude = ('owner', 'is_published',)


class TestPaperForm(forms.ModelForm, StyleFormMixin):
    """Форма для модели TestPaper"""

    class Meta:
        model = TestPaper
        exclude = ('owner', 'is_published',)
        widgets = {
            "description": Textarea(attrs={"cols": 60, "rows": 5}),
        }


class QuestionForm(forms.ModelForm, StyleFormMixin):
    """Форма для модели Question"""

    class Meta:
        model = Question
        fields = ('question_text',)
        widgets = {
            "question_text": Textarea(attrs={"cols": 60, "rows": 5}),
        }


class AnswerForm(forms.ModelForm, StyleFormMixin):
    """Форма для модели Answer"""

    class Meta:
        model = Answer
        fields = ('answer_text', 'is_correct',)
