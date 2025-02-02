from django import forms
from .models import Post, User, Comment


class UserProfileForm(forms.ModelForm):
    """Форма для Юзера."""

    model = User
    fields = ('username', 'first_name', 'last_name', 'emil',)


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