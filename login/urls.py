from django.contrib import admin
from django.urls import path
from login import views
from .views import login_view, RegisterView, VerifyOTPView

urlpatterns = [
    path("login/", login_view, name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
]
