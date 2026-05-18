from django.contrib import admin
from .models import InsightsSubscription, PaystackEventLog


@admin.register(InsightsSubscription)
class InsightsSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["email", "status", "currency", "amount", "paid_at", "next_payment_date"]
    list_filter = ["status", "currency"]
    search_fields = ["email", "reference", "paystack_subscription_code"]
    readonly_fields = ["created_at", "updated_at", "paid_at"]


@admin.register(PaystackEventLog)
class PaystackEventLogAdmin(admin.ModelAdmin):
    list_display = ["event_type", "event_id", "reference", "is_processed", "received_at"]
    list_filter = ["event_type", "is_processed"]
    search_fields = ["event_type", "event_id", "reference"]
    readonly_fields = ["received_at", "processed_at"]
