from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "学生"
        BUSINESS = "business", "経営者"
        ADMIN = "admin", "管理者"

    email = models.EmailField("email address", unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    icon = models.ImageField(upload_to="user_icons/", blank=True, null=True)

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_business(self):
        return self.role == self.Role.BUSINESS

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    def __str__(self):
        return self.username
