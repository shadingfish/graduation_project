import logging

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone
from django.views.generic import View, DeleteView, UpdateView
from django.shortcuts import render, redirect, get_object_or_404
from utils.extracter import extract
from utils.store_data import (
    create_crop,
    create_neo4j_transaction,
    create_genus_family_in_neo4j,
    query_dict,
)
from .models import Crop
from .forms import CropForm, FileUploadForm  # 假设你有一个名为 CropForm 的 ModelForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import json
import pandas as pd

logger = logging.getLogger(__name__)


class Neo4jManagerMixin(UserPassesTestMixin):
    def test_func(self):
        return is_neo4j_manager(self.request.user)


def is_neo4j_manager(user):
    return user.groups.filter(name="neo4j_manager").exists()


class CropDeleteView(LoginRequiredMixin, Neo4jManagerMixin, DeleteView):
    model = Crop
    success_url = reverse_lazy("neo4j-manage")  # 删除成功后的重定向URL

    def get_object(self, queryset=None):
        """重写 get_object 来允许使用 latin_name 作为参数"""
        latin_name = self.kwargs.get("latin_name")
        return get_object_or_404(Crop, latin_name=latin_name)

    def delete(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            if request.is_ajax():
                return JsonResponse({"success": True}, status=200)
        except Exception as e:
            if request.is_ajax():
                return JsonResponse({"success": False, "error": str(e)}, status=400)
        return super().delete(request, *args, **kwargs)


class CropUpdateView(LoginRequiredMixin, Neo4jManagerMixin, UpdateView):
    model = Crop
    fields = [
        "latin_name",
        "family_name",
        "genus_name",
        "chinese_name",
        "chinese_family_name",
        "chinese_genus_name",
    ]
    template_name = "neo4j_manage/crop_form.html"  # 指定一个模板文件
    success_url = reverse_lazy("neo4j-manage")

    def get_object(self, queryset=None):
        latin_name = self.kwargs.get("latin_name")
        return get_object_or_404(Crop, latin_name=latin_name)


class CropView(LoginRequiredMixin, Neo4jManagerMixin, View):
    template_name = "neo4j_manage/neo4j_manage.html"
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        # 分页显示作物
        crop_list = Crop.objects.order_by("-last_modified")
        print(crop_list)
        paginator = Paginator(crop_list, self.paginate_by)
        print(paginator)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        print(page_obj)

        # 提供空表单
        form = CropForm()
        return render(request, self.template_name, {"form": form, "page_obj": page_obj})

    def post(self, request, *args, **kwargs):
        form = CropForm(request.POST)
        success_url = reverse_lazy("neo4j-manage")

        if form.is_valid():
            try:
                with transaction.atomic():
                    # Django 数据库操作
                    crop = form.save(commit=False)
                    # Neo4j 数据库操作
                    with create_neo4j_transaction() as session:
                        create_genus_family_in_neo4j(session, crop)
                    # 保存 Django 模型
                    crop.save()
                # 重定向到成功页面或显示成功信息
                return HttpResponseRedirect(success_url)
            except Exception as e:
                form.add_error(None, "Neo4j写入失败，作物保存事务被终止")

        crop_list = Crop.objects.order_by("-last_modified")
        paginator = Paginator(crop_list, self.paginate_by)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        # 表单无效的情况
        return render(request, self.template_name, {"form": form, "page_obj": page_obj})


class FileUploadView(LoginRequiredMixin, Neo4jManagerMixin, View):
    def post(self, request, *args, **kwargs):
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            # 检查文件类型
            if not file.name.endswith((".csv", ".xls", ".xlsx")):
                return JsonResponse({"success": False, "message": "不支持的文件类型"})

            # 尝试处理文件
            try:
                if file.name.endswith(".csv"):
                    return self.handle_csv(file)
                elif file.name.endswith((".xls", ".xlsx")):
                    return self.handle_excel(file)
            except Exception as e:
                return JsonResponse({"success": False, "message": str(e)})
        else:
            return JsonResponse(
                {"success": False, "message": "表单验证失败，检查文件是否上传"}
            )

    def handle_csv(self, file):
        try:
            # 使用 pandas 处理 CSV 以支持更复杂的操作
            df = pd.read_csv(
                file,
                usecols=[
                    "latin_name",
                    "family_name",
                    "genus_name",
                    "chinese_name",
                    "chinese_family_name",
                    "chinese_genus_name",
                ],
            )
            self.process_data(df)
        except Exception as e:
            # 记录异常信息，可使用 logging 模块记录日志
            print(f"Error processing CSV file: {str(e)}")
            # 向上层抛出异常，可选择抛出具体类型的异常或者重新封装异常
            raise Exception("Failed to process CSV file.") from e
        return JsonResponse({"success": True, "message": "CSV 文件上传成功"})

    def handle_excel(self, file):
        try:
            # 使用 pandas 处理 Excel 文件
            df = pd.read_excel(
                file,
                usecols=[
                    "latin_name",
                    "family_name",
                    "genus_name",
                    "chinese_name",
                    "chinese_family_name",
                    "chinese_genus_name",
                ],
            )
            self.process_data(df)
        except Exception as e:
            # 记录异常信息
            print(f"Error processing Excel file: {str(e)}")
            # 向上层抛出异常
            raise Exception("Failed to process Excel file.") from e
        return JsonResponse({"success": True, "message": "Excel 文件上传成功"})

    def process_data(self, df):
        required_columns = [
            "latin_name",
            "family_name",
            "genus_name",
            "chinese_name",
            "chinese_family_name",
            "chinese_genus_name",
        ]

        # 检查必需的列是否含空值
        if df[required_columns].isnull().any().any():
            raise ValidationError("One or more required fields are empty.")

        try:
            with transaction.atomic():  # 外层事务管理所有操作
                for _, row in df.iterrows():
                    # 检查是否已存在具有相同拉丁名的作物
                    if not Crop.objects.filter(latin_name=row["latin_name"]).exists():
                        # 创建作物实例但不立即保存
                        crop = Crop(
                            latin_name=row["latin_name"],
                            family_name=row["family_name"],
                            genus_name=row["genus_name"],
                            chinese_name=row["chinese_name"],
                            chinese_family_name=row["chinese_family_name"],
                            chinese_genus_name=row["chinese_genus_name"],
                        )

                        # Neo4j 数据库操作
                        with create_neo4j_transaction() as session:
                            create_genus_family_in_neo4j(session, crop)

                        # 保存到 Django 数据库
                        crop.save()
                    else:
                        print(f"Skipping duplicate entry for {row['latin_name']}")
        except Exception as e:
            # 处理错误，可以记录错误信息
            print(f"An error occurred: {str(e)}")
            raise e  # 抛出异常，触发事务回滚


@method_decorator(csrf_exempt, name="dispatch")
class FetchAndUpdateView(LoginRequiredMixin, Neo4jManagerMixin, View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        crop_name = data.get("crop_name")

        print("Asking GPT...")
        gpt_data = extract(plant=crop_name)
        print("Querying Neo4j...")
        with create_neo4j_transaction() as session:
            neo4j_data = query_dict(session, crop_name)
            print("Query results:")
            print(neo4j_data)

        return JsonResponse({"gpt_data": gpt_data, "neo4j_data": neo4j_data})


@method_decorator(csrf_exempt, name="dispatch")
class UpdateNeo4jView(LoginRequiredMixin, Neo4jManagerMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            crop_name = data.get("crop_name")
            datadict = data.get("datadict")

            # 根据 crop_name 找到相应的 Crop 实例
            crop_data = json.loads(datadict)
            crop_data = json.loads(crop_data)
            print("uploading data...")
            print(crop_data)
            update_crop_in_neo4j(crop_name, crop_data)

            return JsonResponse({"success": True})

        except Exception as e:
            # 如果捕捉到异常，可以在这里进行日志记录等操作
            # 并返回 False 表示操作失败
            logger.error(f"An error occurred: {e}", exc_info=True)
            return JsonResponse({"success": False})


# 假设的 check, search 和 update_crop_in_neo4j 函数
def check(crop_name):
    print("Running Langchain to collect information about " + crop_name)
    result = extract(plant=crop_name)
    print("Finished. Result: ")
    if result == "no" or len(result) < 50:
        result = "The given word is not a plant."
    else:
        # result = parse_output(result)
        print(result)
    # 实现与 GPT 的交互
    return result


def update_crop_in_neo4j(crop_name, crop_data):
    print("In update_crop_in_neo4j...")
    try:
        # 更新 Neo4j 数据库中的数据...
        with create_neo4j_transaction() as session:
            create_crop(session, crop_data)

        # 现在更新 Django 中的 last_modified 字段
        crop = Crop.objects.get(latin_name=crop_name)
        crop.last_modified = timezone.now()
        crop.is_synced = "Y"
        crop.save()
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        raise e

    # def delete(self, request, *args, **kwargs):
    #     try:
    #         # 获取要删除的对象实例
    #         self.object = self.get_object()
    #
    #         # 调用基类的 delete 方法，这将处理删除逻辑并重定向到 success_url
    #         response = super(CropDeleteView, self).delete(request, *args, **kwargs)
    #
    #         # 如果来自 AJAX 请求，提供 JSON 响应
    #         if request.is_ajax():
    #             return JsonResponse({'success': True})
    #         return response
    #     except PermissionDenied:
    #         # 如果捕获到权限拒绝异常，也给出 JSON 响应
    #         if request.is_ajax():
    #             return JsonResponse({'success': False, 'error': "Permission denied"})
    #         else:
    #             raise  # 对于非 AJAX 请求，重新抛出异常
    #     except Exception as e:
    #         # 处理任何其他异常并提供 JSON 响应
    #         if request.is_ajax():
    #             return JsonResponse({'success': False, 'error': str(e)})
    #         else:
    #             return
    #             # 对于非 AJAX 请求，可以选择重定向或者抛出异常
    #             # return redirect('error_page_url')  # 可以重定向到一个错误页面
