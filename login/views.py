from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from .models import OTP
from .serializers import RegisterSerializer ,SendOTPSerializer , VerifyOTPSerializer , ResetPasswordSerializer,LoginSerializer
from .utils import generate_otp
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
User = get_user_model()

@api_view(['POST'])
def login_api(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {'error': 'Email and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    user = authenticate(username=user.email, password=password)

    if user is None:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    return Response(
        {
            'message': 'Login successful',
            'user_id': user.id,
            'email': user.email,
            # 'username': user.username
        },
        status=status.HTTP_200_OK
    )

class SendOTPView(APIView):
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.get(email=email)

        if not User.objects.filter(email=email).exists():
            return Response(
                {"error": "Email not registered"},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp = generate_otp()
        OTP.objects.create(
            user=user,
            otp=otp
        )

        send_mail(
            "Password Reset OTP",
            f"Your OTP is {otp}",
            "noreply@example.com",
            [email],
        )

        return Response({"message": "OTP sent successfully"})

class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]
        new_password = serializer.validated_data["new_password"]
        confirm_password = serializer.validated_data["confirm_password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        otp_obj = OTP.objects.filter(user=user).order_by('-created_at').first()
        print(otp_obj)
        if not otp_obj:
            return Response(
                {"error": "OTP not found"},
                status=status.HTTP_400_BAD_REQUEST
            )
        otp_isverified = otp_obj.is_verified
        print(otp_isverified)
        if otp_isverified != True:
            return Response(
                {"message": "OTP is not verified"},
                status=status.HTTP_200_OK,
        )
        user.set_password(new_password)  # ✅ correct way
        user.save()
        return Response(
            {"message": "Password reset successful"},
            status=status.HTTP_200_OK,
        )

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
        print(user)

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
