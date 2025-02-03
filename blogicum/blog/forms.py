from django import forms
from .models import Post, User, Comment


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
        widget = forms.DateInput(attrs={'type': 'date'}),

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {'text': forms.Textarea(
                attrs={'rows': 3, 'cols': 5})
        }