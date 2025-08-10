from django.shortcuts import render, redirect, HttpResponse
from .models import Image
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


# Create your views here.
def index(request):
    images = Image.objects.all().order_by("-id")
    context = {"images": images}
    return render(request, "index.html", context)


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            messages.error(request, "Password doesn't match")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            User.objects.create_user(username=username, email=email, password=password2)
            messages.success(request, "Account Created Successfully!")
            return redirect("login_page")
    return render(request, "signup.html")


def login_page(request):
    username = request.POST.get("username")
    password = request.POST.get("password")

    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        messages.success(request, "Logged In Successfully!")
        return redirect("index")
    else:
        # messages.error(request, "Invalid username or password")
        return redirect("login_page")
    return render(request, "login.html")


def upload(request):
    if request.method == "POST":
        image_title = request.POST.get("title")
        image = request.FILES.get("image")
        if image:
            Image.objects.create(title=image_title, image=image)
            messages.success(request, "Uploaded Successfully!")
            return redirect("index")
        else:
            messages.error(request, "Not Uploaded")
            return redirect("upload")
    return render(request, "upload.html")


def logout_page(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!")
    return redirect("index")
