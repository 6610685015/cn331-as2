from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class UserViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # สร้าง user เอาไว้ใช้ test login/logout
        self.user = User.objects.create_user(
            username="testuser",
            password="12345",
            first_name="Test",
            email="test@example.com"
        )

    # ----- index view -----
    def test_index_redirect_if_not_logged_in(self):
        """ถ้า user ไม่ login ต้อง redirect ไปหน้า Login"""
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse("Login")))

    def test_index_loads_if_logged_in(self):
        """ถ้า login แล้วควรเปิดหน้า home ได้"""
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "room/home.html")

    # ----- login view -----
    def test_login_view_get(self):
        """เรียกหน้า login แบบ GET ควรโหลด template"""
        response = self.client.get(reverse("Login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")

    def test_login_view_post_success(self):
        """login สำเร็จควร redirect ไปหน้า home"""
        response = self.client.post(reverse("Login"), {
            "username": "testuser",
            "password": "12345",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))

    def test_login_view_post_fail(self):
        """login ผิดต้องขึ้นข้อความ error"""
        response = self.client.post(reverse("Login"), {
            "username": "testuser",
            "password": "wrongpassword",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid credentials.")

    # ----- logout view -----
    def test_logout_view(self):
        response = self.client.get(reverse("Logout"))
        self.assertContains(response, "You're Logout", html=True)  

    # ----- register view -----
    def test_register_view_get(self):
        """เรียกหน้า register แบบ GET"""
        response = self.client.get(reverse("Register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")

    def test_register_view_post_success(self):
        """register สำเร็จ"""
        response = self.client.post(reverse("Register"), {
            "Username": "newuser",
            "Password": "abc123",
            "confirm_password": "abc123",
            "first_name": "New",
            "email": "new@example.com",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Register success")
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_view_post_password_mismatch(self):
        """ถ้า password ไม่ตรงกัน ต้อง return error"""
        response = self.client.post(reverse("Register"), {
            "Username": "newuser",
            "Password": "abc123",
            "confirm_password": "wrongpass",
            "first_name": "New",
            "email": "new@example.com",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password not match")

    def test_register_view_post_username_exists(self):
        """ถ้า username ซ้ำต้อง return error"""
        response = self.client.post(reverse("Register"), {
            "Username": "testuser",  # ซ้ำกับ user ใน setUp
            "Password": "12345",
            "confirm_password": "12345",
            "first_name": "Test",
            "email": "test@example.com",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already registry")
