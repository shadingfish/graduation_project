from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import View, UpdateView
from django.contrib.auth.views import LoginView
from .forms import UserRegisterForm, UserUpdateForm


class SignUpView(SuccessMessageMixin, generic.CreateView):
    template_name = "accounts/signup.html"
    form_class = UserRegisterForm
    success_url = reverse_lazy("login")
    success_message = "Your profile was created successfully!"


class UserLoginView(LoginView):
    template_name = "accounts/login.html"

    def form_valid(self, form):
        # 调用父类的 form_valid 方法进行登录
        super().form_valid(form)

        user = form.get_user()
        # 检查用户是否为管理员
        if user.groups.filter(name="neo4j_manager").exists():
            # 设置 session 在浏览器关闭时过期
            self.request.session.set_expiry(0)

        messages.success(self.request, "登录成功！")  # 添加成功消息

        # 返回一个 HttpResponseRedirect 对象
        return HttpResponseRedirect(self.get_success_url())


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("profile")

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        if "delete_account" in request.POST:
            logout(request)
            request.user.delete()
            return redirect("login")
        return super().post(request, *args, **kwargs)
