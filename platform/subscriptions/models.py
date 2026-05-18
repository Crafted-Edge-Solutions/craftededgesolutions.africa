from django.conf import settings
from django.db import models
from django.db.models import Q

from core.models import TimeStampedModel


class PaystackEventLog(models.Model):
    event_type = models.CharField(max_length=120)
    event_id = models.CharField(max_length=120, blank=True)
    reference = models.CharField(max_length=120, blank=True)
    payload = models.JSONField(default=dict)
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    is_processed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-received_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["event_type", "event_id"],
                condition=~Q(event_id=""),
                name="subs_unique_paystack_event_type_id",
            )
        ]

    def __str__(self):
        return f"{self.event_type} — {self.reference}"


class InsightsSubscription(TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_ACTIVE = "active"
    STATUS_CANCELLED = "cancelled"
    STATUS_EXPIRED = "expired"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending payment"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_EXPIRED, "Expired"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="insights_subscription",
    )
    email = models.EmailField()
    currency = models.CharField(max_length=3, default="KES")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=80, unique=True)
    paystack_subscription_code = models.CharField(max_length=120, blank=True)
    paystack_customer_code = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    next_payment_date = models.DateField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} — {self.status}"

    @property
    def is_active(self):
        return self.status == self.STATUS_ACTIVE
