from django.shortcuts import  get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from blog.models import Post, User, Category, Comment
from . forms import PostForm, UserProfileForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin

NUM_ON_MAIN = 10


class OnlyAuthorMixin(UserPassesTestMixin):  # Миксин только для автора

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user



class MaintListView(ListView): # Красава работяга, работает, НЕ ТРОГАТЬ111!!
    """Класс отвечающий за отображение постов на главной странице"""
    model = Post
    template_name = 'blog/index.html'  # Ведет на главную страницу и отображает все опубликованные посты
    context_object_name = 'page_obj'  # Имя переменной в контексте, которое будет использоваться в шаблоне
    paginate_by = NUM_ON_MAIN  # Количество постов на странице

    def get_queryset(self):
        """Переопределяем метод для фильтрации и аннотации постов с использованием кастомного менеджера."""
        return Post.objects.published().select_related(
            'category', 'location', 'author'
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')



"""Классы отвечающие за профиль."""


class ProfileListView(ListView):  # Отображает профиль  нормально не работает. Постоянно ошибки

    model = Post
    template_name = 'blog/profile.html'
    paginate_by = NUM_ON_MAIN

    def get_queryset(self):
        username = self.kwargs["username"]
        self.author = get_object_or_404(User, username=username)
        return Post.objects.filter(author=self.author)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = get_object_or_404(
            User, username=self.kwargs["username"]
        )
        return context


class EditProfileView(OnlyAuthorMixin, UpdateView):
    model = User  # Для редактирования профиля(нет редактирования потому что я не существует профиля)
    form_class = UserProfileForm
    template_name = 'blog/user.html'

    def test_func(self):
        # Получаем текущий объект.
        object = self.get_object()
        # Метод вернёт True или False.
        # Если пользователь - автор объекта, то тест будет пройден.
        # Если нет, то будет вызвана ошибка 403.
        return object.author == self.request.user

    def dispatch(self, request, *args, **kwargs):
        self.user = get_object_or_404(User, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)





"""Классы отвечающие за посты"""


class PostCreateView(LoginRequiredMixin, CreateView): # Заебись работает норм. НЕ ТРОГАТЬ!!11
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


class PostDetailView(DetailView): # Не работаеть, пофиксить(Удаление, редактирование и читать дальше не работает че за хуйня??)
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user





class PostCategoryListView(ListView):#не работает изза эдит пост, созависимая тварь
    model = Post
    template_name = "blog/category.html"

    def get_queryset(self):
        slug = self.kwargs["slug"]
        self.category = get_object_or_404(Category, slug=slug, is_published=True)
        return Post.objects.filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class PostUpdateView(OnlyAuthorMixin, UpdateView):#не работает изза эдит пост, созависимая тварь
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect("blog:post_detail", pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.object.pk})  # Используем pk объекта


class PostDeleteView(OnlyAuthorMixin, DeleteView):# ХЗ работает или нет, но вроде из-за сук выше не видно работы этого мелкого
    model = Post
    template_name = 'blog/comment.html'
    def get_success_url(self):
        return reverse('blog:index')  # Перенаправление на главную страницу после удаления

"""Классы для комментов"""

class CommentCreateView(CreateView):
    pass

class CommentDeleteview(DeleteView):
    pass









'''class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    ordering = 'id'

    def get_queryset(self):
        return Post.published_posts
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post"] = self.object_list
        return context'''
