# Generated by Django 4.2.9 on 2024-01-13 03:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Crop",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("latin_name", models.CharField(max_length=255, unique=True)),
                ("last_modified", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="QueryHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("query_content", models.TextField()),
                ("timestamp", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="query_histories",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]