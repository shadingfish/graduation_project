from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserRegisterForm


class UserAdmin(BaseUserAdmin):
    add_form = UserRegisterForm
    # 添加用户时显示的字段
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "email",
                    "first_name",
                    "last_name",
                ),
            },
        ),
    )
    # 编辑用户时显示的字段
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["username", "email", "first_name", "last_name", "is_staff"]
    list_filter = ["groups", "email", "first_name", "last_name", "is_staff"]
    search_fields = ("username", "first_name", "last_name", "email")


# 注册 User 和 Group 模型到 Django admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
# admin.site.register(Group)
