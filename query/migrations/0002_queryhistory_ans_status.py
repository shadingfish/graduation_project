# Generated by Django 4.2.10 on 2024-04-24 04:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("query", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="queryhistory",
            name="ans_status",
            field=models.CharField(
                choices=[
                    ("KG", "Knowledge Graph"),
                    ("LLM", "Large Language Model"),
                    ("F", "Failed"),
                ],
                default="F",
                max_length=3,
            ),
        ),
    ]
