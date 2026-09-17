from django.contrib import admin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("spot", "user", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("comment_text",)
