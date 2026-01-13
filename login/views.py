from django.shortcuts import render,HttpResponse
from login.models import login
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from .models import User, OTP
from .serializers import RegisterSerializer
from .utils import generate_otp

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=email,   # using email as username
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")  # change as needed
        else:
            messages.error(request, "Invalid email or password")

    return render(request, "login.html")


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        user.is_active = False
        user.save()

        otp_code = generate_otp()
        OTP.objects.create(user=user, otp=otp_code)

        # Send OTP via email (for Postman testing)
        send_mail(
            subject="Verify your account",
            message=f"Your OTP is {otp_code}",
            from_email="noreply@example.com",
            recipient_list=[user.email],
        )

        return Response(
            {"message": "Registration successful. OTP sent."},
            status=status.HTTP_201_CREATED
        )


class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp_input = request.data.get("otp")

        if not email or not otp_input:
            return Response(
                {"error": "Email and OTP are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
            otp_obj = OTP.objects.filter(
                user=user,
                otp=otp_input,
                is_verified=False
            ).latest("created_at")

        except (User.DoesNotExist, OTP.DoesNotExist):
            return Response(
                {"error": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp_obj.is_expired():
            return Response(
                {"error": "OTP expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp_obj.is_verified = True
        otp_obj.save()

        user.is_active = True
        user.save()

        return Response(
            {"message": "OTP verified successfully"},
            status=status.HTTP_200_OK
        )
