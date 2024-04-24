from django import forms
from django.forms import Textarea

from comments.models import Comment
from materials.forms import StyleFormMixin


class CommentForm(forms.ModelForm, StyleFormMixin):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            "text": Textarea(attrs={"cols": 120, "rows": 5}),
        }
