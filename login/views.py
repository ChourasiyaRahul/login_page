from django.shortcuts import render,HttpResponse
from login.models import login

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

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
