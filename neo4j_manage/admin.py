from django.contrib import admin
from .models import Crop


class CropAdmin(admin.ModelAdmin):
    list_display = (
        "latin_name",
        "family_name",
        "chinese_name",
        "chinese_family_name",
        "chinese_genus_name",
        "last_modified",
        "is_synced",
    )
    list_filter = (
        "family_name",
        "genus_name",
        "chinese_family_name",
        "chinese_genus_name",
        "last_modified",
        "is_synced",
    )
    search_fields = (
        "latin_name",
        "family_name",
        "genus_name",
        "chinese_name",
        "chinese_family_name",
        "chinese_genus_name",
    )
    readonly_fields = ("last_modified",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "latin_name",
                    "family_name",
                    "genus_name",
                    "chinese_name",
                    "is_synced",
                )
            },
        ),
        (
            "Advanced options",
            {
                "classes": ("collapse",),
                "fields": (
                    "chinese_family_name",
                    "chinese_genus_name",
                    "last_modified",
                ),
            },
        ),
    )


admin.site.register(Crop, CropAdmin)

# Register your models here.
