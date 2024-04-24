from django.db import models


class Crop(models.Model):
    SYNC_CHOICES = (
        ("Y", "Yes"),
        ("N", "No"),
    )

    latin_name = models.CharField(max_length=255, unique=True)
    family_name = models.CharField(max_length=255)
    genus_name = models.CharField(max_length=255)
    chinese_name = models.CharField(max_length=255)
    chinese_family_name = models.CharField(max_length=255)
    chinese_genus_name = models.CharField(max_length=255)
    last_modified = models.DateTimeField(auto_now=True)
    is_synced = models.CharField(max_length=1, choices=SYNC_CHOICES, default="N")

    def __str__(self):
        return f"{self.latin_name} - {self.last_modified.strftime('%Y-%m-%d %H:%M:%S')}"
