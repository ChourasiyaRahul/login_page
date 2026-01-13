from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class login(models.Model):
    email= models.EmailField(max_length=122)
    password= models.CharField( max_length=122)
 
# Create your models here.
class register(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField(max_length=20)
    phone = PhoneNumberField(max_length=10)
    organization = models.CharField(max_length=20)
    password = models.CharField(max_length=10)
    confirm_password = models.CharField(max_length=10)
    otp = models.CharField(max_length=4)
