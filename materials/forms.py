from django import forms
from django.forms import Textarea

from materials.models import Subject, Theme, Lesson, Comment


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class SubjectForm(forms.ModelForm, StyleFormMixin):
    class Meta:
        model = Subject
        fields = '__all__'


class ThemeForm(forms.ModelForm, StyleFormMixin):
    class Meta:
        model = Theme
        exclude = ('owner', 'is_published',)


class LessonForm(forms.ModelForm, StyleFormMixin):
    class Meta:
        model = Lesson
        exclude = ('owner', 'is_published',)


class CommentForm(forms.ModelForm, StyleFormMixin):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            "text": Textarea(attrs={"cols": 120, "rows": 5}),
        }
