from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
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
from .forms import CropForm  # 假设你有一个名为 CropForm 的 ModelForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import json


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
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    # def get_success_url(self):
    #     # 如果您需要在成功删除后执行某些操作，可以在这里定义
    #     return reverse_lazy('neo4j-manage')


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
        success_url = reverse_lazy('neo4j-manage')

        
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
            return JsonResponse({"success": False})


# 假设的 check, search 和 update_crop_in_neo4j 函数
@login_required
@user_passes_test(is_neo4j_manager)
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
    # 更新 Neo4j 数据库中的数据...
    with create_neo4j_transaction() as session:
        create_crop(session, crop_data)

    # 现在更新 Django 中的 last_modified 字段
    crop = Crop.objects.get(latin_name=crop_name)
    crop.last_modified = timezone.now()
    crop.save()
