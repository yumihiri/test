from django.contrib import admin

from .models import Category, Spot


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon_class", "color", "student_registrable")
    list_filter = ("student_registrable",)


@admin.action(description="選択したスポットを承認する")
def approve_spots(modeladmin, request, queryset):
    queryset.update(status=Spot.Status.APPROVED, reject_reason="")


@admin.action(description="選択したスポットを却下する")
def reject_spots(modeladmin, request, queryset):
    queryset.update(status=Spot.Status.REJECTED)


@admin.register(Spot)
class SpotAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "status", "registered_by", "created_at")
    list_filter = ("status", "category")
    search_fields = ("name", "address")
    actions = [approve_spots, reject_spots]
