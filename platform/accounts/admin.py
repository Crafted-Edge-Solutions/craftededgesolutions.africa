from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Insights Membership", {"fields": ("is_insights_member", "paystack_customer_code")}),
    )
    list_display = ["email", "username", "is_insights_member", "is_staff", "date_joined"]
    list_filter = ["is_insights_member", "is_staff", "is_active"]
