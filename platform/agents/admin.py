from django.contrib import admin
from django.utils.html import format_html

from .models import Conversation, KnowledgeEntry, Message, Tenant


class KnowledgeEntryInline(admin.TabularInline):
    model = KnowledgeEntry
    extra = 1
    fields = ("category", "question", "answer", "is_active")


class ConversationInline(admin.TabularInline):
    model = Conversation
    extra = 0
    readonly_fields = ("customer_phone", "started_at", "last_message_at", "is_escalated", "is_resolved")
    fields = readonly_fields
    can_delete = False
    max_num = 0
    show_change_link = True


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("business_name", "slug", "plan", "is_active", "whatsapp_phone_number_id", "conversations_count", "created_at")
    list_filter = ("plan", "is_active")
    search_fields = ("business_name", "slug", "whatsapp_phone_number_id")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at",)
    inlines = [KnowledgeEntryInline, ConversationInline]

    fieldsets = (
        ("Identity", {"fields": ("name", "slug", "owner", "plan", "is_active", "created_at")}),
        ("Business Profile", {"fields": ("business_name", "business_description", "mpesa_paybill", "mpesa_account")}),
        ("WhatsApp API", {"fields": ("whatsapp_phone_number_id",)}),
        ("Agent Behaviour", {"fields": ("welcome_message", "fallback_message", "system_prompt_addon")}),
        ("Escalation", {"fields": ("escalation_phone", "escalation_message_template")}),
        ("Business Hours", {"fields": ("timezone", "business_hours", "outside_hours_message")}),
    )

    def conversations_count(self, obj):
        return obj.conversations.count()
    conversations_count.short_description = "Conversations"


@admin.register(KnowledgeEntry)
class KnowledgeEntryAdmin(admin.ModelAdmin):
    list_display = ("tenant", "category", "question_preview", "is_active", "created_at")
    list_filter = ("tenant", "category", "is_active")
    search_fields = ("question", "answer", "tenant__business_name")

    def question_preview(self, obj):
        return obj.question[:80]
    question_preview.short_description = "Question"


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("direction", "body", "timestamp", "is_escalation_trigger")
    fields = readonly_fields
    can_delete = False
    max_num = 0
    ordering = ("timestamp",)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("tenant", "customer_phone", "started_at", "last_message_at", "is_escalated", "is_resolved")
    list_filter = ("tenant", "is_escalated", "is_resolved")
    search_fields = ("customer_phone", "customer_name", "tenant__business_name")
    readonly_fields = ("tenant", "customer_phone", "started_at", "last_message_at")
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "direction", "body_preview", "timestamp", "is_escalation_trigger")
    list_filter = ("direction", "is_escalation_trigger")
    search_fields = ("body", "conversation__customer_phone")
    readonly_fields = ("whatsapp_message_id", "timestamp", "created_at")

    def body_preview(self, obj):
        return obj.body[:80]
    body_preview.short_description = "Body"
