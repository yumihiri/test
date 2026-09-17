from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from reviews.models import Comment
from spots.models import Category, Spot


class SpotFlowTests(TestCase):
    def setUp(self):
        self.business = User.objects.create_user(
            username="biz", email="biz@example.com", password="pass12345", role=User.Role.BUSINESS
        )
        self.student = User.objects.create_user(
            username="stu", email="stu@example.com", password="pass12345", role=User.Role.STUDENT
        )
        self.admin = User.objects.create_user(
            username="adm", email="adm@example.com", password="pass12345", role=User.Role.ADMIN, is_staff=True
        )
        self.other_business = User.objects.create_user(
            username="biz2", email="biz2@example.com", password="pass12345", role=User.Role.BUSINESS
        )
        self.food_category, _ = Category.objects.get_or_create(
            name="安い飯屋",
            defaults={"icon_class": "🍜", "color": "#D97706", "student_registrable": False},
        )
        self.atm_category, _ = Category.objects.get_or_create(
            name="ATM",
            defaults={"icon_class": "💴", "color": "#2F6F4E", "student_registrable": True},
        )

    def test_business_can_register_any_category(self):
        self.client.login(username="biz", password="pass12345")
        response = self.client.post(
            reverse("spots:register"),
            {
                "name": "テスト食堂",
                "address": "水戸市宮町1-1-1",
                "category": self.food_category.id,
                "description": "テスト",
                "latitude": "36.3418",
                "longitude": "140.4468",
            },
        )
        self.assertEqual(response.status_code, 302)
        spot = Spot.objects.get(name="テスト食堂")
        self.assertEqual(spot.status, Spot.Status.PENDING)
        self.assertEqual(spot.registered_by, self.business)

    def test_student_cannot_register_business_only_category(self):
        self.client.login(username="stu", password="pass12345")
        response = self.client.post(
            reverse("spots:register"),
            {
                "name": "学生が登録した食堂",
                "address": "水戸市宮町1-1-1",
                "category": self.food_category.id,
                "description": "テスト",
                "latitude": "36.3418",
                "longitude": "140.4468",
            },
        )
        self.assertEqual(response.status_code, 200)  # フォームエラーで再表示
        self.assertFalse(Spot.objects.filter(name="学生が登録した食堂").exists())

    def test_student_can_register_no_owner_category(self):
        self.client.login(username="stu", password="pass12345")
        response = self.client.post(
            reverse("spots:register"),
            {
                "name": "駅前ATM",
                "address": "水戸市宮町1-1-1",
                "category": self.atm_category.id,
                "description": "テスト",
                "latitude": "36.3418",
                "longitude": "140.4468",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Spot.objects.filter(name="駅前ATM").exists())

    def test_pending_spot_hidden_from_map_for_others(self):
        spot = Spot.objects.create(
            name="非公開スポット",
            address="住所",
            latitude="36.0",
            longitude="140.0",
            category=self.food_category,
            registered_by=self.business,
            status=Spot.Status.PENDING,
        )
        self.client.login(username="stu", password="pass12345")
        response = self.client.get(reverse("spots:map"))
        payload = response.context["spots"]
        self.assertNotIn(spot.id, [s["id"] for s in payload])

        # 管理者には見える
        self.client.logout()
        self.client.login(username="adm", password="pass12345")
        response = self.client.get(reverse("spots:map"))
        payload = response.context["spots"]
        self.assertIn(spot.id, [s["id"] for s in payload])

    def test_review_duplicate_blocked(self):
        spot = Spot.objects.create(
            name="公開スポット",
            address="住所",
            latitude="36.0",
            longitude="140.0",
            category=self.food_category,
            registered_by=self.business,
            status=Spot.Status.APPROVED,
        )
        self.client.login(username="stu", password="pass12345")
        url = reverse("reviews:submit", args=[spot.id])
        self.client.post(url, {"rating": 5, "comment_text": "最高"})
        self.assertEqual(Comment.objects.filter(spot=spot, user=self.student).count(), 1)

        self.client.post(url, {"rating": 3, "comment_text": "二回目"})
        self.assertEqual(Comment.objects.filter(spot=spot, user=self.student).count(), 1)

    def test_business_can_delete_own_spot(self):
        spot = Spot.objects.create(
            name="自分のスポット",
            address="住所",
            latitude="36.0",
            longitude="140.0",
            category=self.food_category,
            registered_by=self.business,
            status=Spot.Status.APPROVED,
        )
        self.client.login(username="biz", password="pass12345")
        response = self.client.post(reverse("spots:delete", args=[spot.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Spot.objects.filter(id=spot.id).exists())

    def test_business_cannot_delete_others_spot(self):
        spot = Spot.objects.create(
            name="他人のスポット",
            address="住所",
            latitude="36.0",
            longitude="140.0",
            category=self.food_category,
            registered_by=self.other_business,
            status=Spot.Status.APPROVED,
        )
        self.client.login(username="biz", password="pass12345")
        response = self.client.post(reverse("spots:delete", args=[spot.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Spot.objects.filter(id=spot.id).exists())

    def test_student_cannot_delete_any_spot(self):
        spot = Spot.objects.create(
            name="削除対象外",
            address="住所",
            latitude="36.0",
            longitude="140.0",
            category=self.atm_category,
            registered_by=self.student,
            status=Spot.Status.APPROVED,
        )
        self.client.login(username="stu", password="pass12345")
        response = self.client.post(reverse("spots:delete", args=[spot.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Spot.objects.filter(id=spot.id).exists())

    def test_anonymous_delete_redirects_to_login(self):
        spot = Spot.objects.create(
            name="未ログインテスト",
            address="住所",
            latitude="36.0",
            longitude="140.0",
            category=self.food_category,
            registered_by=self.business,
            status=Spot.Status.APPROVED,
        )
        response = self.client.post(reverse("spots:delete", args=[spot.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
        self.assertTrue(Spot.objects.filter(id=spot.id).exists())

    def test_admin_can_delete_any_spot(self):
        spot = Spot.objects.create(
            name="管理者が消せるスポット",
            address="住所",
            latitude="36.0",
            longitude="140.0",
            category=self.food_category,
            registered_by=self.business,
            status=Spot.Status.APPROVED,
        )
        self.client.login(username="adm", password="pass12345")
        response = self.client.post(reverse("spots:delete", args=[spot.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Spot.objects.filter(id=spot.id).exists())

    def test_admin_bulk_approve_action(self):
        spot = Spot.objects.create(
            name="承認待ちスポット",
            address="住所",
            latitude="36.0",
            longitude="140.0",
            category=self.food_category,
            registered_by=self.business,
            status=Spot.Status.PENDING,
        )
        self.admin.is_superuser = True
        self.admin.save()
        self.client.login(username="adm", password="pass12345")
        response = self.client.post(
            reverse("admin:spots_spot_changelist"),
            {
                "action": "approve_spots",
                "_selected_action": [spot.id],
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        spot.refresh_from_db()
        self.assertEqual(spot.status, Spot.Status.APPROVED)
