from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from accounts.models import BusinessVerification, User

TEST_ACCOUNTS = [
    {
        "username": "student1",
        "password": "Student123!",
        "email": "student1@example.com",
        "role": User.Role.STUDENT,
    },
    {
        "username": "business1",
        "password": "Business123!",
        "email": "business1@example.com",
        "role": User.Role.BUSINESS,
    },
    {
        "username": "admin1",
        "password": "Admin123!",
        "email": "admin1@example.com",
        "role": User.Role.ADMIN,
        "is_staff": True,
        "is_superuser": True,
    },
]


class Command(BaseCommand):
    help = "動作確認用の固定パスワードのテストアカウント（学生・経営者・管理者）を作成する"

    def handle(self, *args, **options):
        for data in TEST_ACCOUNTS:
            username = data["username"]
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": data["email"],
                    "role": data["role"],
                    "is_staff": data.get("is_staff", False),
                    "is_superuser": data.get("is_superuser", False),
                },
            )
            user.set_password(data["password"])
            user.role = data["role"]
            user.is_staff = data.get("is_staff", False)
            user.is_superuser = data.get("is_superuser", False)
            user.save()
            status = "作成" if created else "更新"
            self.stdout.write(f"{status}: {username} / {data['password']} ({data['role']})")

        business_user = User.objects.get(username="business1")
        verification, _ = BusinessVerification.objects.get_or_create(
            user=business_user,
            defaults={
                "business_name": "テスト経営者商店",
                "representative_name": "テスト太郎",
                "corporate_number": "1234567890123",
                "contact_email": "business1@example.com",
                "id_document": ContentFile(b"test", name="test_id.txt"),
            },
        )
        verification.status = BusinessVerification.Status.APPROVED
        verification.reject_reason = ""
        verification.save()
        self.stdout.write("business1 の承認申請を承認済みにしました（スポット登録可）")

        self.stdout.write(self.style.SUCCESS("テストアカウントの準備が完了しました。"))
        self.stdout.write("")
        self.stdout.write("  学生:   student1 / Student123!")
        self.stdout.write("  経営者: business1 / Business123!（承認済み・スポット登録可）")
        self.stdout.write("  管理者: admin1 / Admin123!（/admin/ にログイン可）")
