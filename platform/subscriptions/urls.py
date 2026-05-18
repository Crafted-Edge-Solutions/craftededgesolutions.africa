from django.urls import path
from . import views

app_name = "subscriptions"

urlpatterns = [
    path("subscribe/", views.subscribe, name="subscribe"),
    path("callback/", views.subscribe_callback, name="callback"),
    path("webhook/paystack/", views.paystack_webhook, name="paystack_webhook"),
]
