from django.db import models
from django.utils import timezone


class PostQuerySet(models.QuerySet):
    def published(self):
        """Возвращает опубликованные посты."""
        return self.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )


class PostManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def published(self):
        """Возвращает опубликованные посты."""
        return self.get_queryset().published()
