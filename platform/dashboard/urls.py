from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("billing/", views.billing, name="billing"),
    path("profile/", views.profile, name="profile"),
    path("change-password/", views.change_password, name="change_password"),
]
