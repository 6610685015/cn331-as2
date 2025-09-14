from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


# หน้าหลัก
def index(request):
    if not request.user.is_authenticated:
        return redirect("Login")

    return render(request, "room/home.html")


# ใช้ login
def login_views(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            # admin:index เป็น url ที่ Django กำหนดไว้ให้เป็นหน้า admin page
            # return redirect(reverse("admin:index"))

            return redirect("home")  # return render(request, "room/home.html")

        else:
            return render(
                request, "users/login.html", {"message": "Invalid credentials."}
            )
    return render(request, "users/login.html")


# ใช้เมื่อมีการ logout
def logout_views(request):
    logout(request)
    context = {"message": "You're Logout"}
    return render(request, "users/login.html", context)


# ใช้สำหรับ register
def register_views(request):
    if request.method == "POST":
        username = request.POST["Username"]
        password = request.POST["Password"]
        first_name = request.POST["first_name"]
        email = request.POST["email"]
        password_again = request.POST["confirm_password"]

        if password != password_again:
            return render(
                request,
                "users/register.html",
                {"message": "Password not match, Please try again."},
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                "users/register.html",
                {"message": "This Username already registry, Please try again."},
            )
        User.objects.create_user(
            username=username, password=password, first_name=first_name, email=email
        )
        return render(
            request,
            "users/login.html",
            {"registry": "Register success"},
        )
    return render(request, "users/register.html")
