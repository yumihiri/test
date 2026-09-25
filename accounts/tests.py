from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import BusinessVerification, User


def make_id_document():
    return SimpleUploadedFile("id.pdf", b"dummy-pdf-content", content_type="application/pdf")


class BusinessVerificationFlowTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="adm", email="adm@example.com", password="pass12345",
            role=User.Role.ADMIN, is_staff=True, is_superuser=True,
        )

    def test_business_signup_redirects_to_verification(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "newbiz",
                "email": "newbiz@example.com",
                "role": User.Role.BUSINESS,
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertRedirects(response, reverse("accounts:business_verification"))
        user = User.objects.get(username="newbiz")
        self.assertFalse(user.is_verified_business)

    def test_student_signup_redirects_to_map(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "newstu",
                "email": "newstu@example.com",
                "role": User.Role.STUDENT,
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertRedirects(response, reverse("spots:map"))

    def test_unverified_business_cannot_access_spot_register(self):
        User.objects.create_user(
            username="biz", email="biz@example.com", password="pass12345", role=User.Role.BUSINESS
        )
        self.client.login(username="biz", password="pass12345")
        response = self.client.get(reverse("spots:register"))
        self.assertRedirects(response, reverse("accounts:business_verification"))

    def test_business_can_submit_verification_and_admin_can_approve(self):
        user = User.objects.create_user(
            username="biz", email="biz@example.com", password="pass12345", role=User.Role.BUSINESS
        )
        self.client.login(username="biz", password="pass12345")
        response = self.client.post(
            reverse("accounts:business_verification"),
            {
                "business_name": "水戸フルーツ製菓会社",
                "representative_name": "山田 太郎",
                "corporate_number": "1234567890123",
                "contact_email": "contact@example.com",
                "id_document": make_id_document(),
            },
        )
        self.assertRedirects(response, reverse("accounts:business_verification"))
        verification = BusinessVerification.objects.get(user=user)
        self.assertEqual(verification.status, BusinessVerification.Status.PENDING)
        self.assertFalse(user.is_verified_business)

        # まだ承認待ちなのでスポット登録できない
        response = self.client.get(reverse("spots:register"))
        self.assertRedirects(response, reverse("accounts:business_verification"))

        # 管理者が承認
        self.client.logout()
        self.client.login(username="adm", password="pass12345")
        response = self.client.post(
            reverse("admin:accounts_businessverification_changelist"),
            {
                "action": "approve_verifications",
                "_selected_action": [verification.id],
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.is_verified_business)

        # 承認後はスポット登録画面に到達できる
        self.client.logout()
        self.client.login(username="biz", password="pass12345")
        response = self.client.get(reverse("spots:register"))
        self.assertEqual(response.status_code, 200)

    def test_rejected_verification_can_be_resubmitted(self):
        user = User.objects.create_user(
            username="biz", email="biz@example.com", password="pass12345", role=User.Role.BUSINESS
        )
        BusinessVerification.objects.create(
            user=user,
            business_name="旧事業者名",
            representative_name="旧代表者",
            corporate_number="1111111111111",
            contact_email="old@example.com",
            id_document=make_id_document(),
            status=BusinessVerification.Status.REJECTED,
            reject_reason="書類が不鮮明です",
        )
        self.client.login(username="biz", password="pass12345")

        # 却下されている場合はフォームが表示される
        response = self.client.get(reverse("accounts:business_verification"))
        self.assertContains(response, "却下")
        self.assertContains(response, "書類が不鮮明です")

        response = self.client.post(
            reverse("accounts:business_verification"),
            {
                "business_name": "新事業者名",
                "representative_name": "新代表者",
                "corporate_number": "2222222222222",
                "contact_email": "new@example.com",
                "id_document": make_id_document(),
            },
        )
        self.assertRedirects(response, reverse("accounts:business_verification"))
        verification = BusinessVerification.objects.get(user=user)
        self.assertEqual(verification.status, BusinessVerification.Status.PENDING)
        self.assertEqual(verification.business_name, "新事業者名")
