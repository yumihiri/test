from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_staff", "date_joined")
    list_filter = ("role", "is_staff", "is_superuser")
    fieldsets = UserAdmin.fieldsets + (
        ("学生生活マップ", {"fields": ("role", "icon")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("学生生活マップ", {"fields": ("role", "icon")}),
    )
