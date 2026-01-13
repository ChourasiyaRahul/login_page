from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class login(models.Model):
    email= models.EmailField(max_length=122)
    password= models.CharField( max_length=122)
 
# ---------------- USER MANAGER ----------------
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # 🔐 secure hashing
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


# ---------------- USER MODEL ----------------
class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    phone = PhoneNumberField(unique=True)
    organization = models.CharField(max_length=20)

    registered_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)

    # Django required fields
    is_active = models.BooleanField(default=False)  # activated after OTP
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["name", "phone", "organization"]

    class Meta:
        db_table = "user"

    def __str__(self):
        return self.email


# ---------------- OTP MODEL ----------------
class OTP(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="otps"
    )
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "otp"
        ordering = ["-created_at"]

    def is_expired(self):
        expiry_time = self.created_at + timedelta(minutes=5)
        return timezone.now() > expiry_time

    def __str__(self):
        return f"{self.user.email} - {self.otp}"

