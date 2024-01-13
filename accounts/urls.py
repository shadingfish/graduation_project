from django.urls import path
from .views import SignUpView, UserLoginView, ProfileView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
