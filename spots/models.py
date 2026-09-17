from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon_class = models.CharField(
        max_length=50, help_text="地図ピン表示に使う絵文字やアイコン識別子（例: 🍜）"
    )
    color = models.CharField(
        max_length=7, default="#2F6F4E", help_text="地図ピンの色（例: #2F6F4E）"
    )
    student_registrable = models.BooleanField(
        default=False,
        help_text="経営者が存在しないカテゴリ（ATM・バス停・トイレ等）。学生ロールでも登録できる。",
    )

    class Meta:
        verbose_name = "カテゴリ"
        verbose_name_plural = "カテゴリ"
        ordering = ["id"]

    def __str__(self):
        return self.name


class Spot(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "承認待ち"
        APPROVED = "approved", "承認済み"
        REJECTED = "rejected", "却下"

    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="spots"
    )
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="spot_images/", blank=True, null=True)
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="registered_spots",
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    reject_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "スポット"
        verbose_name_plural = "スポット"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def is_visible_to(self, user):
        if self.status == self.Status.APPROVED:
            return True
        if not user.is_authenticated:
            return False
        if user.role == "admin":
            return True
        return self.registered_by_id == user.id

    def can_be_deleted_by(self, user):
        if not user.is_authenticated:
            return False
        if user.role == "admin":
            return True
        return user.role == "business" and self.registered_by_id == user.id
