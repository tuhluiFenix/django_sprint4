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

    def annotated(self):
        return self.annotate(
            comment_count=models.Count('comments')
        ).order_by('-pub_date').select_related(
            'category', 'author', 'location',
        )
