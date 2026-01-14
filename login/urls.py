from django.urls import path
from login import views
from .views import RegisterView, VerifyOTPView
from .views import (
    login_api,
    SendOTPView,
    VerifyOTPView,
    ResetPasswordView
)

urlpatterns = [    
    path('login/', login_api, name='login-api'),
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('resetpassword/', ResetPasswordView.as_view(), name='reset-password'),
]

