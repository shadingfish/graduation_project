# Generated by Django 4.2.9 on 2024-01-13 07:14

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

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
                ("genus_name", models.CharField(max_length=255)),
                ("chinese_name", models.CharField(max_length=255)),
                ("chinese_family_name", models.CharField(max_length=255)),
                ("chinese_genus_name", models.CharField(max_length=255)),
                ("last_modified", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]