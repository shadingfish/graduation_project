from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.


class QueryHistory(models.Model):
    ANSWER_STATUS_CHOICES = (
        ("KG", "Knowledge Graph"),
        ("LLM", "Large Language Model"),
        ("F", "Failed"),
        ("E", "Exception"),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="query_histories"
    )
    query_content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    ans_status = models.CharField(
        max_length=3, choices=ANSWER_STATUS_CHOICES, default="F"
    )

    def __str__(self):
        return f"{self.user.username} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


# Create your models here.
