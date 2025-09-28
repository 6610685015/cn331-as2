from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_views, name="Login"),
    path("login/", views.login_views, name="Login"),
    path("logout/", views.logout_views, name="Logout"),
    path("home/", views.index, name="home"),
    path("index/", views.index, name="index"),
    path("register/", views.register_views, name="Register"),
]

