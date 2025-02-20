from django.shortcuts import get_object_or_404, redirect
from django.utils.timezone import now

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    DetailView,
    DeleteView,
    CreateView,
    ListView,
    UpdateView
)

from .forms import CommentForm, PostForm, UserProfileForm
from blog.models import Category, Comment, Post, User
from . mixins import CommentEditMixin, OnlyAuthorMixin

NUM_ON_MAIN = 10


class MaintListView(ListView):
    """Класс отвечающий за отображение постов на главной странице"""

    model = Post
    template_name = "blog/index.html"
    paginate_by = NUM_ON_MAIN  # Количество постов на странице

    def get_queryset(self):
        """
        Переопределяем метод для фильтрации и аннотации постов
        с использованием кастомного менеджера.
        """
        return self.model.objects.published().annotated()


class ProfileListView(ListView):
    model = User
    template_name = "blog/profile.html"
    context_object_name = "profile"
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


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "blog/user.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        username = self.request.user
        return reverse("blog:profile", kwargs={"username": username})


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание поста, назначение автора и вывод usename."""

    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user.username
        return reverse("blog:profile", kwargs={"username": username})


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detail.html"

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
            id=self.kwargs["pk"],
        )


class PostCategoryListView(MaintListView):
    model = Category
    template_name = "blog/category.html"

    def current_category(self):
        return get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True)

    def get_queryset(self):
        return self.current_category().posts.published().annotated()

    def get_context_data(self, **kwargs):
        # Добавляет посты в контекст для использования в шаблонах
        context = super().get_context_data(**kwargs)
        context["category"] = self.current_category()
        return context


class PostUpdateView(OnlyAuthorMixin, LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect("blog:post_detail", pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.object.pk})


class PostDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    model = Post
    template_name = "blog/create.html"
    success_url = reverse_lazy("blog:index")
    queryset = Post.objects.select_related("author", "location", "category")

    def delete(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs["pk"])
        if self.request.user != post.author:
            return redirect("blog:index")

        return super().delete(request, *args, **kwargs)


class CommentCreateView(CommentEditMixin, LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs["pk"])
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentUpdateView(OnlyAuthorMixin, CommentEditMixin, UpdateView):
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


class CommentDeleteView(CommentEditMixin, OnlyAuthorMixin, DeleteView):
    model = Comment
    pk_url_kwarg = "comment_pk"
    template_name = "blog/comment.html"

    def delete(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=self.kwargs["comment_pk"])
        if self.request.user != comment.author:
            return redirect("blog:post_detail", pk=self.kwargs["pk"])
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Удаляем объект формы из контекста
        context.pop("form", None)
        return context
