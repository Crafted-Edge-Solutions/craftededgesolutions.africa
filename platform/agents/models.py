import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone


class Tenant(models.Model):
    PLAN_STARTER = "starter"
    PLAN_GROWTH = "growth"
    PLAN_BUSINESS = "business"
    PLAN_CHOICES = [
        (PLAN_STARTER, "Starter — up to 500 conversations/mo"),
        (PLAN_GROWTH, "Growth — up to 2,000 conversations/mo"),
        (PLAN_BUSINESS, "Business — unlimited"),
    ]

    # Identity
    name = models.CharField(max_length=200, help_text="Internal reference name")
    slug = models.SlugField(unique=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="agent_tenants",
        help_text="CES platform user who manages this tenant's dashboard",
    )

    # Business profile — fed into every agent prompt
    business_name = models.CharField(max_length=200)
    business_description = models.TextField(
        help_text="2–4 sentences: what the business does, who it serves, its tone"
    )
    mpesa_paybill = models.CharField(max_length=30, blank=True)
    mpesa_account = models.CharField(max_length=100, blank=True)

    # WhatsApp API (Meta Cloud API — CES system user token in settings)
    whatsapp_phone_number_id = models.CharField(
        max_length=100, unique=True,
        help_text="Phone Number ID from Meta Business Manager (not the phone number itself)"
    )

    # Agent behaviour
    welcome_message = models.TextField(
        default="Hello! Welcome. How can I help you today?",
        help_text="Sent to new contacts on their first message"
    )
    fallback_message = models.TextField(
        default="I'm having trouble right now. Please try again in a moment or contact us directly.",
        help_text="Sent when AI or API call fails"
    )
    system_prompt_addon = models.TextField(
        blank=True,
        help_text="Extra instructions appended to the base system prompt (product rules, tone, prohibited topics)"
    )

    # Escalation
    escalation_phone = models.CharField(
        max_length=30, blank=True,
        help_text="WhatsApp number to notify on escalation (international format, e.g. 254712345678)"
    )
    escalation_message_template = models.TextField(
        default="⚠️ Escalation from {business_name}\nCustomer: {customer_phone}\nMessage: {last_message}",
    )

    # Business hours — JSON: {"mon":"08:00-18:00","tue":"08:00-18:00",...,"sat":"09:00-14:00","sun":"closed"}
    business_hours = models.JSONField(
        default=dict, blank=True,
        help_text='JSON: {"mon":"08:00-18:00","sat":"09:00-14:00","sun":"closed"}'
    )
    outside_hours_message = models.TextField(
        blank=True,
        help_text="Message sent when a customer contacts outside business hours. Leave blank to always respond."
    )
    timezone = models.CharField(max_length=50, default="Africa/Nairobi")

    # Subscription
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default=PLAN_STARTER)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["business_name"]
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"

    def __str__(self):
        return f"{self.business_name} ({self.slug})"

    @property
    def business_hours_display(self):
        if not self.business_hours:
            return "Open always"
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        parts = []
        for d, label in zip(days, labels):
            hours = self.business_hours.get(d, "closed")
            parts.append(f"{label}: {hours}")
        return " | ".join(parts)

    @property
    def mpesa_info(self):
        if not self.mpesa_paybill:
            return "Not configured"
        info = f"Paybill {self.mpesa_paybill}"
        if self.mpesa_account:
            info += f", Account: {self.mpesa_account}"
        return info

    def is_within_hours(self):
        if not self.business_hours:
            return True
        try:
            import pytz
            tz = pytz.timezone(self.timezone)
            now = timezone.now().astimezone(tz)
            day = now.strftime("%a").lower()
            hours = self.business_hours.get(day, "closed")
            if not hours or hours == "closed":
                return False
            open_str, close_str = hours.split("-")
            open_h, open_m = map(int, open_str.strip().split(":"))
            close_h, close_m = map(int, close_str.strip().split(":"))
            open_t = datetime.time(open_h, open_m)
            close_t = datetime.time(close_h, close_m)
            return open_t <= now.time() < close_t
        except Exception:
            return True

    def conversations_this_month(self):
        now = timezone.now()
        return self.conversations.filter(
            started_at__year=now.year,
            started_at__month=now.month,
        ).count()

    def messages_today(self):
        today = timezone.now().date()
        return Message.objects.filter(
            conversation__tenant=self,
            timestamp__date=today,
        ).count()

    def escalations_this_week(self):
        week_ago = timezone.now() - datetime.timedelta(days=7)
        return self.conversations.filter(is_escalated=True, escalated_at__gte=week_ago).count()


class KnowledgeEntry(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="knowledge")
    category = models.CharField(max_length=100, blank=True, help_text="Optional grouping (e.g. Pricing, Hours, Returns)")
    question = models.TextField(help_text="The question or topic trigger")
    answer = models.TextField(help_text="The answer the agent should give")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "question"]
        verbose_name = "Knowledge Entry"
        verbose_name_plural = "Knowledge Entries"

    def __str__(self):
        return f"[{self.tenant.slug}] {self.question[:60]}"


class Conversation(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="conversations")
    customer_phone = models.CharField(max_length=30, db_index=True)
    customer_name = models.CharField(max_length=200, blank=True)

    is_escalated = models.BooleanField(default=False)
    escalated_at = models.DateTimeField(null=True, blank=True)
    is_resolved = models.BooleanField(default=False)

    started_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = [["tenant", "customer_phone"]]
        ordering = ["-last_message_at"]
        verbose_name = "Conversation"

    def __str__(self):
        return f"{self.tenant.business_name} ↔ {self.customer_phone}"

    @property
    def is_within_24h_window(self):
        cutoff = timezone.now() - datetime.timedelta(hours=24)
        return self.last_message_at >= cutoff

    def last_customer_message(self):
        return self.messages.filter(direction="in").order_by("-timestamp").first()


class Message(models.Model):
    IN = "in"
    OUT = "out"
    DIRECTION_CHOICES = [(IN, "Incoming"), (OUT, "Outgoing")]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    whatsapp_message_id = models.CharField(max_length=200, unique=True, db_index=True)
    direction = models.CharField(max_length=3, choices=DIRECTION_CHOICES)
    body = models.TextField()
    is_escalation_trigger = models.BooleanField(default=False)
    timestamp = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]
        verbose_name = "Message"

    def __str__(self):
        return f"[{self.direction}] {self.body[:60]}"
