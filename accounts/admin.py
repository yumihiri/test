from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import BusinessVerification, User


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


@admin.action(description="選択した申請を承認する")
def approve_verifications(modeladmin, request, queryset):
    queryset.update(status=BusinessVerification.Status.APPROVED, reject_reason="")


@admin.action(description="選択した申請を却下する")
def reject_verifications(modeladmin, request, queryset):
    queryset.update(status=BusinessVerification.Status.REJECTED)


@admin.register(BusinessVerification)
class BusinessVerificationAdmin(admin.ModelAdmin):
    list_display = (
        "business_name",
        "representative_name",
        "user",
        "status",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("business_name", "representative_name", "corporate_number", "user__username")
    actions = [approve_verifications, reject_verifications]
