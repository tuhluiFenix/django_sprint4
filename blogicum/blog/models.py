from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from .managers import PostQuerySet

User = get_user_model()

MAX_LENGTH = 256


class PublishedModel(models.Model):
    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField("Добавлено", auto_now_add=True)

    class Meta:
        abstract = True  # Указываем, что это абстрактная модель


class Category(PublishedModel):
    title = models.CharField("Заголовок", max_length=MAX_LENGTH)
    description = models.TextField("Описание")
    slug = models.SlugField(
        "Идентификатор",
        unique=True,
        help_text="Идентификатор страницы для URL; разрешены "
                  "символы латиницы, цифры, дефис и подчёркивание.",
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title


class Location(PublishedModel):
    name = models.CharField("Название места", max_length=MAX_LENGTH)

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name


class Post(PublishedModel):
    title = models.CharField(
        "Заголовок", max_length=MAX_LENGTH, default="Untitled Post"
    )
    text = models.TextField("Текст", default="No content")
    pub_date = models.DateTimeField(
        "Дата и время публикации",
        default=timezone.now,
        help_text="Если установить дату и время в "
                  "будущем — можно делать отложенные публикации.",
    )
    author = models.ForeignKey(
        User, verbose_name="Автор публикации", on_delete=models.CASCADE
    )
    location = models.ForeignKey(
        Location,
        null=True,
        blank=True,
        verbose_name="Местоположение",
        on_delete=models.SET_NULL,
    )
    category = models.ForeignKey(
        Category,
        null=True,
        verbose_name="Категория",
        on_delete=models.SET_NULL,
    )
    image = models.ImageField("Фото", upload_to="post_images", blank=True)

    objects = PostQuerySet.as_manager()

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        ordering = ("-pub_date",)  # Сортировка по дате публикации в
        # порядке убывания
        default_related_name = "posts"  # Установленное общее имя
        # для всех связанных объектов

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField(
        "Комментарий"
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name="comments"
    )
    created_at = models.DateTimeField(
        auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
