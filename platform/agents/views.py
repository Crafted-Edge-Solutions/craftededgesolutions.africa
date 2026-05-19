import hashlib
import hmac
import json
import logging
import threading
import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, close_old_connections
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Conversation, KnowledgeEntry, Message, Tenant

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Webhook
# ---------------------------------------------------------------------------

def _verify_signature(request) -> bool:
    app_secret = getattr(settings, "WHATSAPP_APP_SECRET", "")
    if not app_secret:
        return True  # skip in dev
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not signature.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(
        app_secret.encode(), request.body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)


@csrf_exempt
def whatsapp_webhook(request):
    if request.method == "GET":
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge", "")
        verify_token = getattr(settings, "WHATSAPP_VERIFY_TOKEN", "")
        if mode == "subscribe" and token == verify_token:
            return HttpResponse(challenge, content_type="text/plain")
        return HttpResponseForbidden("Verification failed")

    if request.method == "POST":
        if not _verify_signature(request):
            logger.warning("WhatsApp webhook: bad signature")
            return HttpResponseForbidden("Bad signature")

        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponse("OK")

        # Return 200 immediately; process in background
        t = threading.Thread(target=_handle_payload, args=(payload,), daemon=True)
        t.start()
        return HttpResponse("OK")

    return HttpResponse("OK")


def _handle_payload(payload: dict) -> None:
    close_old_connections()
    try:
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                if change.get("field") != "messages":
                    continue
                value = change.get("value", {})
                phone_number_id = value.get("metadata", {}).get("phone_number_id", "")

                try:
                    tenant = Tenant.objects.get(
                        whatsapp_phone_number_id=phone_number_id, is_active=True
                    )
                except Tenant.DoesNotExist:
                    logger.warning("No active tenant for phone_number_id: %s", phone_number_id)
                    continue

                for msg in value.get("messages", []):
                    _dispatch_message(tenant, msg)
    except Exception:
        logger.exception("Unhandled error in webhook payload processing")


def _dispatch_message(tenant, msg: dict) -> None:
    from .services.whatsapp import send_message
    from .services.agent import process_incoming_message

    msg_id = msg.get("id", "")
    msg_type = msg.get("type", "")
    sender_phone = msg.get("from", "")

    if not sender_phone or not msg_id:
        return

    # Non-text messages get a polite rejection
    if msg_type != "text":
        send_message(
            tenant.whatsapp_phone_number_id,
            sender_phone,
            "I can only read text messages for now. Please type your question.",
        )
        return

    body = msg.get("text", {}).get("body", "").strip()
    if not body:
        return

    ts = datetime.datetime.fromtimestamp(
        int(msg.get("timestamp", 0)), tz=datetime.timezone.utc
    )

    conversation, _ = Conversation.objects.get_or_create(
        tenant=tenant,
        customer_phone=sender_phone,
        defaults={"started_at": ts},
    )

    # Deduplicate — Meta may deliver the same webhook multiple times
    try:
        message = Message.objects.create(
            conversation=conversation,
            whatsapp_message_id=msg_id,
            direction=Message.IN,
            body=body,
            timestamp=ts,
        )
    except IntegrityError:
        logger.debug("Duplicate message %s — skipped", msg_id)
        return

    Conversation.objects.filter(pk=conversation.pk).update(last_message_at=ts)

    process_incoming_message(tenant, conversation, message)


# ---------------------------------------------------------------------------
# Tenant dashboard (login required — owner sees their own tenant only)
# ---------------------------------------------------------------------------

def _get_tenant_for_user(user, slug):
    if user.is_staff:
        return get_object_or_404(Tenant, slug=slug)
    return get_object_or_404(Tenant, slug=slug, owner=user, is_active=True)


@login_required
def dashboard(request, slug):
    tenant = _get_tenant_for_user(request.user, slug)

    recent_convos = (
        tenant.conversations.prefetch_related("messages")
        .order_by("-last_message_at")[:20]
    )

    ctx = {
        "tenant": tenant,
        "recent_convos": recent_convos,
        "stats": [
            ("Conversations this month", tenant.conversations_this_month(), "total unique customers"),
            ("Messages today", tenant.messages_today(), "in + out"),
            ("Escalations this week", tenant.escalations_this_week(), "needed human agent"),
            ("Knowledge entries", tenant.knowledge.filter(is_active=True).count(), "FAQs loaded"),
        ],
    }
    return render(request, "agents/dashboard.html", ctx)


@login_required
def conversation_detail(request, slug, convo_pk):
    tenant = _get_tenant_for_user(request.user, slug)
    conversation = get_object_or_404(Conversation, pk=convo_pk, tenant=tenant)
    messages = conversation.messages.order_by("timestamp")

    if request.method == "POST" and request.POST.get("action") == "resolve":
        conversation.is_escalated = False
        conversation.is_resolved = True
        conversation.save(update_fields=["is_escalated", "is_resolved"])
        return redirect("agents_dashboard", slug=slug)

    return render(request, "agents/conversation.html", {
        "tenant": tenant,
        "conversation": conversation,
        "messages": messages,
    })


@login_required
def knowledge_list(request, slug):
    tenant = _get_tenant_for_user(request.user, slug)
    entries = tenant.knowledge.order_by("category", "question")
    return render(request, "agents/knowledge.html", {"tenant": tenant, "entries": entries})


@login_required
@require_POST
def knowledge_add(request, slug):
    tenant = _get_tenant_for_user(request.user, slug)
    question = request.POST.get("question", "").strip()
    answer = request.POST.get("answer", "").strip()
    category = request.POST.get("category", "").strip()
    if question and answer:
        KnowledgeEntry.objects.create(
            tenant=tenant, question=question, answer=answer, category=category
        )
    return redirect("agents_knowledge", slug=slug)


@login_required
@require_POST
def knowledge_delete(request, slug, entry_pk):
    tenant = _get_tenant_for_user(request.user, slug)
    KnowledgeEntry.objects.filter(pk=entry_pk, tenant=tenant).delete()
    return redirect("agents_knowledge", slug=slug)


# ---------------------------------------------------------------------------
# CES staff: list all tenants
# ---------------------------------------------------------------------------

@login_required
def tenant_list(request):
    if not request.user.is_staff:
        return redirect("/dashboard/")
    tenants = Tenant.objects.all().order_by("business_name")
    return render(request, "agents/tenant_list.html", {"tenants": tenants})
