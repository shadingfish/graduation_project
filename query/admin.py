from django.contrib import admin
from .models import QueryHistory

# Register your models here.


class QueryHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "ans_status",
        "timestamp",
    )
    list_filter = (
        "user",
        "ans_status",
        "timestamp",
    )
    search_fields = (
        "user",
        "ans_status",
        "timestamp",
    )
    readonly_fields = ("timestamp", "query_content")


admin.site.register(QueryHistory, QueryHistoryAdmin)
