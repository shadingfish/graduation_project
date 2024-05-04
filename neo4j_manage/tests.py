import pytest
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from .models import Crop
from django.contrib.auth.models import User, Group


class CropViewTests(TestCase):
    def setUp(self):
        # 创建测试用户和管理员组
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.group = Group.objects.create(name="neo4j_manager")
        self.user.groups.add(self.group)
        self.client.login(username="testuser", password="12345")
        Crop.objects.create(
            latin_name="TestCrop",
            family_name="TestFamily",
            genus_name="TestGenus",
            chinese_name="测试作物",
            chinese_family_name="测试科",
            chinese_genus_name="测试属",
        )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse("neo4j-manage"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("neo4j-manage"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "neo4j_manage/neo4j_manage.html")


class CropUpdateViewTests(TestCase):
    def setUp(self):
        # 创建一个用户和管理员组，并登录
        self.user = User.objects.create_user(username="admin", password="12345")
        self.group = Group.objects.create(name="neo4j_manager")
        self.user.groups.add(self.group)
        self.client.login(username="admin", password="12345")

        # 创建一个作物实例用于更新
        self.crop = Crop.objects.create(
            latin_name="OriginalName",
            family_name="FamilyName",
            genus_name="Genus",
            chinese_name="ChineseName",
            chinese_family_name="ChineseFamilyName",
            chinese_genus_name="ChineseGenusName",
        )
        self.update_url = reverse("crop_update", kwargs={"latin_name": "OriginalName"})

    def test_crop_update_with_valid_data(self):
        response = self.client.post(
            self.update_url,
            {
                "latin_name": "UpdatedName",
                "family_name": "UpdatedFamilyName",
                "genus_name": "UpdatedGenus",
                "chinese_name": "UpdatedChineseName",
                "chinese_family_name": "UpdatedChineseFamilyName",
                "chinese_genus_name": "UpdatedChineseGenusName",
            },
        )
        self.assertRedirects(response, reverse("neo4j-manage"))
        updated_crop = Crop.objects.get(id=self.crop.id)
        self.assertEqual(updated_crop.latin_name, "UpdatedName")

    def test_crop_update_with_invalid_data(self):
        response = self.client.post(
            self.update_url,
            {
                "latin_name": "",
                "family_name": "UpdatedFamilyName",
                "genus_name": "UpdatedGenus",
                "chinese_name": "UpdatedChineseName",
                "chinese_family_name": "UpdatedChineseFamilyName",
                "chinese_genus_name": "UpdatedChineseGenusName",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "latin_name", "This field is required.")


class CropDeleteViewTests(TestCase):
    def setUp(self):
        # 设置测试数据和环境
        self.admin_user = User.objects.create_user(username="admin", password="12345")
        self.group = Group.objects.create(name="neo4j_manager")
        self.admin_user.groups.add(self.group)
        self.client.login(username="admin", password="12345")

        self.crop = Crop.objects.create(
            latin_name="ToDelete",
            family_name="Family",
            genus_name="Genus",
            chinese_name="ChineseName",
            chinese_family_name="ChineseFamilyName",
            chinese_genus_name="ChineseGenusName",
        )
        self.delete_url = reverse("crop_delete", kwargs={"latin_name": "ToDelete"})

    def test_crop_delete(self):
        # 确保请求删除操作
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, reverse("neo4j-manage"))

        # 使用 assertRaises 检查 DoesNotExist 异常
        with self.assertRaises(Crop.DoesNotExist):
            Crop.objects.get(latin_name="ToDelete")

    def test_crop_delete_with_wrong_user(self):
        # 使用一个非管理员用户尝试进行删除操作
        self.client.logout()
        wrong_user = User.objects.create_user(username="wronguser", password="12345")
        self.client.login(username="wronguser", password="12345")
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 403)  # 期待 403 禁止访问错误

    # @pytest.mark.django_db
    # @pytest.mark.parametrize(
    #     "file_name, file_path, expected_status, expected_message",
    #     [
    #         ("test_excels.csv", "test/test_data/test_excels.csv", 200, "success"),
    #         ("empty_excels.csv", "test/test_data/empty_excels.csv", 200, "success"),
    #         ("test_excels.xlsx", "test/test_data/test_excels.xlsx", 200, "success"),
    #         ("test_words.txt", "test/test_data/test_words.txt", 200, "不支持的文件类型"),
    #     ]
    # )
    # @override_settings(MEDIA_ROOT="/tmp/")
    # def test_file_upload_variations(self, client, file_name, file_path, expected_status, expected_message):
    #     with open(file_path, "rb") as fp:
    #         response = client.post(reverse("upload-crop-file"), {"file": fp})
    #         assert response.status_code == expected_status
    #         assert expected_message in response.json()["message"]


# @override_settings(MEDIA_ROOT='/tmp/')  # Temporarily override MEDIA_ROOT for file handling in tests
# class FileUploadViewTests(TestCase):
#     @pytest.mark.parametrize("file_name, file_path, expected_status, expected_message", [
#         ("test_excels.csv", "test/test_data/test_excels.csv", 200, "success"),
#         ("empty_excels.csv", "test/test_data/empty_excels.csv", 200, "success"),
#         ("test_excels.xlsx", "test/test_data/test_excels.xlsx", 200, "success"),
#         ("test_words.txt", "test/test_data/test_words.txt", 200, "不支持的文件类型"),
#     ])
#     def test_file_upload_variations(self, file_name, file_path, expected_status, expected_message):
#         with open(file_path, 'rb') as fp:
#             response = self.client.post(reverse('upload-crop-file'), {'file': fp})
#         assert response.status_code == expected_status
#         assert expected_message in response.json()['message']


class PyTestFileUpload:
    def __init__(self):
        self.user = None

    def setUp(self):
        self.user = User.objects.create_user(
            "testuser", "test@example.com", "testpassword"
        )

    def test_not_permitted_file_upload(self, client):
        client.login(username="testuser", password="testpassword")
        with open("test/test_data/empty_excels.csv", "rb") as fp:
            response = client.post(reverse("upload-crop-file"), {"file": fp})
            assert response.status_code == 403
            assert "fail" in response.json()["message"]

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "file_name, file_path, expected_status, expected_message",
        [
            ("test_excels.csv", "test/test_data/test_excels.csv", 200, "success"),
            ("empty_excels.csv", "test/test_data/empty_excels.csv", 200, "success"),
            ("test_excels.xlsx", "test/test_data/test_excels.xlsx", 200, "success"),
            (
                "test_words.txt",
                "test/test_data/test_words.txt",
                200,
                "不支持的文件类型",
            ),
        ],
    )
    @override_settings(MEDIA_ROOT="/tmp/")
    def test_neo4j_file_upload_variations(
        self, client, file_name, file_path, expected_status, expected_message
    ):
        # 确保neo4j_manager组存在
        group, created = Group.objects.get_or_create(name="neo4j_manager")
        # 将用户添加到neo4j_manager组
        group.user_set.add(self.user)
        # 登录
        client.login(username="testuser", password="testpassword")

        with open(file_path, "rb") as fp:
            response = client.post(reverse("upload-crop-file"), {"file": fp})
            assert response.status_code == expected_status
            assert expected_message in response.json()["message"]
