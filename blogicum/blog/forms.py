from django import forms

from .models import Comment, Post, User


ROWS = 3
COLS = 5


class UserProfileForm(forms.ModelForm):
    """Форма для Юзера."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email")


class PostForm(forms.ModelForm):
    """Форма для постов."""

    class Meta:
        """Абстракный класс."""

        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local', 'class': 'form-control'},
            )
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(
                attrs={'rows': ROWS, 'cols': COLS})
        }
