from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from blog.models import Post, User, Category, Comment
from . forms import PostForm, UserProfileForm, CommentForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.utils.timezone import now

NUM_ON_MAIN = 10


class OnlyAuthorMixin(UserPassesTestMixin):  # Миксин только для автора

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class CommentEditMixin:  # миксин для комментов
    model = Comment
    pk_url_kwarg = "comment_pk"
    template_name = "blog/comment.html"


class MaintListView(ListView): # Красава работяга, работает, НЕ ТРОГАТЬ111!!
    """Класс отвечающий за отображение постов на главной странице"""
    model = Post
    template_name = 'blog/index.html'  # Ведет на главную страницу и отображает все опубликованные посты
    paginate_by = NUM_ON_MAIN  # Количество постов на странице

    def get_queryset(self):
        """Переопределяем метод для фильтрации и аннотации постов
        с использованием кастомного менеджера."""
        return self.model.objects.published().annotated()


"""Классы отвечающие за профиль."""


class ProfileListView(ListView):  # Информация о пользователе доступна всем посетителям сайта
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    paginate_by = NUM_ON_MAIN

    def get_user(self):
        username = self.kwargs["username"]
        return get_object_or_404(User, username=username)

    def get_queryset(self):
        author = self.get_user()
        posts = author.posts.annotated()
        if self.request.user == author:
            return posts
        return posts.published()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.get_user()
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):  # Редактирование профиля доступно только для залогиненного пользователя, хозяина аккаунта
    model = User
    form_class = UserProfileForm
    template_name = "blog/user.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        username = self.request.user
        return reverse("blog:profile", kwargs={"username": username})


"""Классы отвечающие за посты"""


class PostCreateView(LoginRequiredMixin, CreateView):  # Для зарегистрированных пользователей
    """Создание поста, назначение автора и вывод usename."""
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user  # Устанавливаем автора
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user.username
        return reverse('blog:profile', kwargs={"username": username})


class PostDetailView(DetailView):  # доступно для всех пользователей
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = (
            self.get_object().comments.select_related("author")
        )
        return context

    def get_object(self, queryset=None):
        post = super().get_object()
        if post.author == self.request.user:
            return post
        return get_object_or_404(
            Post,
            is_published=True,
            category__is_published=True,
            pub_date__lte=now(),
            id=self.kwargs['pk'],
        )


class PostCategoryListView(MaintListView):  # Публикации пользователя доступны все посетителям
    model = Category
    template_name = "blog/category.html"

    def current_category(self):
        return get_object_or_404(Category, slug=self.kwargs['category_slug'], is_published=True)

    def get_queryset(self):
        return self.current_category().posts.published().annotated()

    def get_context_data(self, **kwargs):
        # Добавляет посты в контекст для использования в шаблонах
        context = super().get_context_data(**kwargs)
        context['category'] = self.current_category()
        return context


class PostUpdateView(OnlyAuthorMixin, LoginRequiredMixin, UpdateView):  # Работает хорошо, но причем тут планета Земля??
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect("blog:post_detail", pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.object.pk})  # Используем pk объекта


class PostDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):  # Работает и молодец и возвращает на главную
    model = Post
    template_name = "blog/create.html"
    success_url = reverse_lazy("blog:index")
    queryset = Post.objects.select_related("author", "location", "category")

    def delete(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs["pk"])
        if self.request.user != post.author:
            return redirect("blog:index")

        return super().delete(request, *args, **kwargs) # Перенаправление на главную страницу после удаления


"""Классы для комментов"""

class CommentCreateView(CommentEditMixin, LoginRequiredMixin, CreateView):  # Создание комментариев только для зарегистрироанных пользователей
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs["pk"])
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.kwargs["pk"]})


class CommentUpdateView(OnlyAuthorMixin, CommentEditMixin, UpdateView):  # работает как надо, красава
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(
            Comment, pk=self.kwargs["comment_pk"]
        )
        if (
            self.request.user
            != comment.author
        ):
            return redirect("blog:post_detail", pk=self.kwargs["pk"])

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.kwargs["pk"]})


class CommentDeleteView(OnlyAuthorMixin, DeleteView):  # работяга работаем метро Люблино
    model = Comment
    pk_url_kwarg = "comment_pk"
    template_name = "blog/comment.html"

    def delete(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=self.kwargs["comment_pk"])
        if self.request.user != comment.author:
            return redirect("blog:post_detail", pk=self.kwargs["pk"])
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.kwargs["pk"]})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Удаляем объект формы из контекста
        context.pop('form', None)
        return context
