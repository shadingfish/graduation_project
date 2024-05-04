import pytest
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.contrib.auth import get_user_model
from pytest import mark


class UserAccountTests(TestCase):
    def setUp(self):
        # 创建测试用户和管理员组
        self.user = User.objects.create_user(
            username="normal", email="normal@user.com", password="12345"
        )
        self.admin_group = Group.objects.create(name="neo4j_manager")
        self.admin = User.objects.create_user(
            username="admin", email="admin@user.com", password="admin123"
        )
        self.admin.groups.add(self.admin_group)

        # URL设置
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.profile_url = reverse("profile")

    def test_login_success(self):
        response = self.client.post(
            self.login_url, {"username": "normal", "password": "12345"}
        )
        self.assertRedirects(response, self.profile_url)

    def test_login_failure(self):
        response = self.client.post(
            self.login_url, {"username": "normal", "password": "wrongpass"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            "Please enter a correct username and password." in response.content.decode()
        )

    def test_admin_login_session_expiry(self):
        response = self.client.post(
            self.login_url, {"username": "admin", "password": "admin123"}
        )
        self.assertRedirects(response, self.profile_url)
        self.assertEqual(
            self.client.session.get_expiry_age(), 604800
        )  # Session 应该在浏览器关闭时过期

    def test_logout(self):
        self.client.login(username="normal", password="12345")
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.login_url)


class PyTestUserLogin:
    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "username,password,expected_redirect,expected_status",
        [
            ("normal", "12345", True, 200),  # 登录成功，重定向到profile页面
            ("wronguser", "nopass", False, 200),  # 登录失败，返回登录页面
            ("admin", "admin123", True, 200),  # 登录成功，重定向到profile页面
            ("normal", "wrongpass", False, 200),  # 登录失败，返回登录页面
            ("", "12345", False, 200),  # 登录失败，返回登录页面
            ("normal", "", False, 200),  # 登录失败，返回登录页面
            ("", "", False, 200),  # 登录失败，返回登录页面
        ],
    )
    def test_login_variations(
        self,
        client,
        username,
        password,
        expected_redirect,
        expected_status,
    ):
        login_url = reverse("login")
        profile_url = reverse("profile")
        response = client.post(login_url, {"username": username, "password": password})
        # 检查状态码
        assert response.status_code == expected_status
