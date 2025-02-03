from django.shortcuts import  get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from blog.models import Post, User, Category, Comment
from . forms import PostForm, UserProfileForm, CommentForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
from blog.managers import PostManager, PostQuerySet

NUM_ON_MAIN = 10


class OnlyAuthorMixin(UserPassesTestMixin):  # Миксин только для автора

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user
    
class CommentEditMixin: # миксин для комментов
    model = Comment
    pk_url_kwarg = "comment_pk"
    template_name = "blog/comment.html"


class MaintListView(ListView): # Красава работяга, работает, НЕ ТРОГАТЬ111!!
    """Класс отвечающий за отображение постов на главной странице"""
    model = Post
    template_name = 'blog/index.html'  # Ведет на главную страницу и отображает все опубликованные посты
    context_object_name = "post_list"  # Имя переменной в контексте, которое будет использоваться в шаблоне
    paginate_by = NUM_ON_MAIN  # Количество постов на странице

    def get_queryset(self):
        """Переопределяем метод для фильтрации и аннотации постов с использованием кастомного менеджера."""
        return Post.objects.published().select_related(
            'category', 'location', 'author'
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')



"""Классы отвечающие за профиль."""


class ProfileListView(MaintListView):  # Информация о пользователе доступна всем посетителям сайта
    context_object_name = 'posts'
    model = Post
    template_name = 'blog/profile.html'


    def get_queryset(self):
        username = self.kwargs["username"]
        self.author = get_object_or_404(User, username=username)
        return super().get_queryset().filter(author=self.author).annotate(comment_count=Count("comments")).order_by('-pub_date')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.author
        return context

class EditProfileView(LoginRequiredMixin, UpdateView):# Редактирование профиля доступно только для залогиненного пользователя, хозяина аккаунта
    model = User
    form_class = UserProfileForm
    template_name = "blog/user.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        username = self.request.user
        return reverse("blog:profile", kwargs={"username": username})





"""Классы отвечающие за посты"""


class PostCreateView(LoginRequiredMixin, CreateView): # Для зарегистрированных пользователей
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
    

class PostDetailView(DetailView): # доступно для всех пользователей
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = (
            self.get_object().comments.prefetch_related("author").all()
        )
        return context

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "comments",
            )
        )





class PostCategoryListView(MaintListView, ListView):# Публикации пользователя доступны все посетителям
    model = Post
    template_name = "blog/category.html"
    context_object_name = "post_list"
    paginate_by = NUM_ON_MAIN

    def get_queryset(self):
        # возвращает категорию слаг
        slug = self.kwargs['category_slug'] #если категори слаг то отображается список постов в определенной категории
        self.category = get_object_or_404(Category, slug=slug)
        # Фильтрует посты по категориям
        return Post.objects.filter(category=self.category).annotate(comment_count=Count('comments')).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        # Добавляет посты в контекст для использования в шаблонах
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context



class PostUpdateView(OnlyAuthorMixin, LoginRequiredMixin, UpdateView):# Работает хорошо, но причем тут планета Земля??
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect("blog:post_detail", pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.object.pk})  # Используем pk объекта


class PostDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):# Работает и молодец и возвращает на главную
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

class CommentCreateView(CommentEditMixin, LoginRequiredMixin, CreateView): #Создание комментариев только для зарегистрироанных пользователей
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs["pk"])
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.kwargs["pk"]})





class CommentUpdateView(OnlyAuthorMixin, CommentEditMixin, UpdateView):# работает как надо, красава
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        if (
            self.request.user
            != Comment.objects.get(pk=self.kwargs["comment_pk"]).author
        ):
            return redirect("blog:post_detail", pk=self.kwargs["pk"])

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.kwargs["pk"]})
    



class CommentDeleteView(OnlyAuthorMixin, CommentEditMixin, DeleteView):# работяга работаем метро Люблино

    def delete(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=self.kwargs["comment_pk"])
        if self.request.user != comment.author:
            return redirect("blog:post_detail", pk=self.kwargs["pk"])
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.kwargs["pk"]})