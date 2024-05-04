from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from django.contrib.auth.models import User
from query.models import QueryHistory
from query.views import QueryView


# Create your tests here.
class QueryViewTests(TestCase):
    def setUp(self):
        # 创建用户
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client = Client()
        self.client.login(username="testuser", password="12345")

        # 创建一些查询历史记录
        QueryHistory.objects.create(
            user=self.user, query_content="Query 1", ans_status="KG"
        )
        QueryHistory.objects.create(
            user=self.user, query_content="Query 2", ans_status="LLM"
        )

        # URL
        self.query_url = reverse("query-page")

    def test_get_query_page(self):
        # 测试 GET 请求
        response = self.client.get(self.query_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "query/main_query.html")
        self.assertEqual(len(response.context["recent_queries"]), 2)

    def test_post_query_page(self):
        # 测试 POST 请求
        response = self.client.post(
            self.query_url, {"search_query": "hello world", "gptActive": "true"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("您的请求正在处理，请稍候...", response.content.decode())
        self.assertTrue(
            QueryHistory.objects.filter(query_content="hello world").exists()
        )

    # 测试无效的登录情况
    # 确保当用户未登录时，视图返回适当的响应。
    def test_get_query_page_without_login(self):
        # 清空所有 session 表明用户未登录
        self.client.logout()
        response = self.client.get(self.query_url)
        # 假设未登录用户应该被重定向到登录页面
        self.assertRedirects(
            response, "{}?next={}".format(reverse("login"), reverse("query-page"))
        )

    # 测试无效的POST数据
    # 验证当POST请求中的数据不完整或格式错误时，视图如何响应。
    def test_post_query_page_with_invalid_data(self):
        # 发送无效数据
        response = self.client.post(
            self.query_url, {"search_query": "", "gptActive": "true"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("您的请求正在处理，请稍候...", response.content.decode())
        # 验证数据库中没有添加新的历史记录
        self.assertFalse(QueryHistory.objects.filter(query_content="").exists())

    # # 测试边界情况
    # # 测试应用边界条件，如查询历史记录数量的极限情况。
    # def test_query_page_with_maximum_history_limit(self):
    #     # 假设最多显示 10 条历史记录
    #     for i in range(15):
    #         QueryHistory.objects.create(
    #             user=self.user, query_content=f"Query {i + 3}", ans_status="KG"
    #         )
    #     response = self.client.get(self.query_url)
    #     self.assertEqual(len(response.context["recent_queries"]), 10)
    #     self.assertNotIn("Query 1", response.content.decode())  # 确保最早的记录不显示
