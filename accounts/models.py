from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
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

    @property
    def is_verified_business(self):
        verification = getattr(self, "business_verification", None)
        return bool(verification and verification.status == BusinessVerification.Status.APPROVED)

    def __str__(self):
        return self.username


corporate_number_validator = RegexValidator(
    regex=r"^\d{13}$", message="法人番号は13桁の数字で入力してください。"
)


class BusinessVerification(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "審査中"
        APPROVED = "approved", "認証済み"
        REJECTED = "rejected", "却下"

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="business_verification"
    )
    business_name = models.CharField("事業者名", max_length=100)
    representative_name = models.CharField("代表者名", max_length=100)
    corporate_number = models.CharField(
        "法人番号", max_length=13, validators=[corporate_number_validator]
    )
    contact_email = models.EmailField("連絡先メールアドレス")
    id_document = models.FileField("本人確認書類", upload_to="business_verifications/")
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    reject_reason = models.TextField("却下理由", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "承認申請"
        verbose_name_plural = "承認申請"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.business_name}（{self.user.username}）"
