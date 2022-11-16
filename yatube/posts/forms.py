from django import forms
from django.contrib.auth import get_user_model

from posts.models import Comment, Post

User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'group': 'группа',
            'text': 'текст',
        }
        help_text = {
            'group': 'Выберите группу для новой записи',
            'text': 'Добавьте текст для новой записи',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'текст',
        }
