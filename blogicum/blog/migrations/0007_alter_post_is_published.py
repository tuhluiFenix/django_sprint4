# Generated by Django 3.2.16 on 2025-02-04 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_alter_post_author_alter_post_category_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='is_published',
            field=models.BooleanField(default=False, verbose_name='Опубликован'),
        ),
    ]
