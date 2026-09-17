from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from spots.models import Spot


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, related_name="comments")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "コメント"
        verbose_name_plural = "コメント"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "spot"], name="unique_review_per_user_spot")
        ]

    def __str__(self):
        return f"{self.spot.name} - {self.user.username} ({self.rating})"
