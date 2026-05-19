import datetime
import json
import logging
import os
import uuid
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.utils import timezone

logger = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

BASE_SYSTEM = """You are a professional customer service agent for {business_name}.

About the business:
{business_description}

Your role:
- Answer questions accurately using the knowledge base below
- Help customers with orders, bookings, and payments
- Respond in the same language the customer uses (English or Swahili)
- Be concise — WhatsApp messages should be short and easy to read
- Never invent information not in your knowledge base

Payment (M-Pesa):
{mpesa_info}

Business hours:
{hours}
{hours_status}

Knowledge base:
---
{knowledge}
---

Special commands (output exactly as shown when needed):
- [ESCALATE] — include this anywhere in your reply when the customer needs human help or has a complex complaint
- Do NOT mention [ESCALATE] to the customer; just include it silently in your message

{custom_instructions}

Today: {datetime}"""


def _build_system_prompt(tenant, knowledge_text: str, within_hours: bool) -> str:
    now = timezone.now()

    hours_status = ""
    if not within_hours and tenant.outside_hours_message:
        hours_status = (
            f"\n⚠️ IMPORTANT: It is currently OUTSIDE business hours. "
            f"Inform the customer politely: {tenant.outside_hours_message}"
        )

    return BASE_SYSTEM.format(
        business_name=tenant.business_name,
        business_description=tenant.business_description,
        mpesa_info=tenant.mpesa_info,
        hours=tenant.business_hours_display,
        hours_status=hours_status,
        knowledge=knowledge_text or "No specific FAQs loaded yet.",
        custom_instructions=tenant.system_prompt_addon or "",
        datetime=now.strftime("%A, %d %B %Y, %I:%M %p EAT"),
    )


def _get_knowledge_text(tenant, query: str) -> str:
    entries = list(tenant.knowledge.filter(is_active=True).values("question", "answer", "category"))
    if not entries:
        return ""

    query_words = {w.lower() for w in query.split() if len(w) > 2}

    def score(entry):
        text = f"{entry['question']} {entry['answer']}".lower()
        return sum(1 for w in query_words if w in text)

    entries.sort(key=score, reverse=True)

    # Always include top 12 entries (high scorers first, then fill rest)
    selected = entries[:12]
    lines = []
    for e in selected:
        prefix = f"[{e['category']}] " if e["category"] else ""
        lines.append(f"Q: {prefix}{e['question']}\nA: {e['answer']}")
    return "\n\n".join(lines)


def _call_groq(messages: list) -> str:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")

    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "max_tokens": 400,
        "temperature": 0.35,
    }).encode()

    req = Request(
        GROQ_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read())
        return data["choices"][0]["message"]["content"]


def process_incoming_message(tenant, conversation, incoming_message) -> None:
    """
    Core agent loop. Called from background thread — must handle all errors internally.
    """
    from .whatsapp import send_message, mark_as_read, send_escalation_notification
    from ..models import Message

    # Mark as read (shows double tick to customer)
    mark_as_read(tenant.whatsapp_phone_number_id, incoming_message.whatsapp_message_id)

    # Don't respond to escalated conversations (human has taken over)
    if conversation.is_escalated and not conversation.is_resolved:
        return

    within_hours = tenant.is_within_hours()

    # Outside hours with a configured message → skip AI entirely
    if not within_hours and tenant.outside_hours_message:
        reply_body = tenant.outside_hours_message
        escalate = False
    else:
        # Build message history (last 16 messages within 24h window)
        cutoff = timezone.now() - datetime.timedelta(hours=24)
        recent = list(
            conversation.messages
            .filter(timestamp__gte=cutoff)
            .order_by("timestamp")
            .values("direction", "body")
        )

        history = [
            {"role": "user" if m["direction"] == "in" else "assistant", "content": m["body"]}
            for m in recent
        ]

        knowledge_text = _get_knowledge_text(tenant, incoming_message.body)
        system_prompt = _build_system_prompt(tenant, knowledge_text, within_hours)

        messages_payload = [{"role": "system", "content": system_prompt}] + history

        try:
            raw_reply = _call_groq(messages_payload)
        except (HTTPError, URLError, RuntimeError) as exc:
            logger.error("Groq error for tenant %s: %s", tenant.slug, exc)
            raw_reply = tenant.fallback_message

        escalate = "[ESCALATE]" in raw_reply
        reply_body = raw_reply.replace("[ESCALATE]", "").strip()

    # First message from this customer → prepend welcome
    if conversation.messages.filter(direction="out").count() == 0 and tenant.welcome_message:
        reply_body = f"{tenant.welcome_message}\n\n{reply_body}".strip()

    # Persist outgoing message
    Message.objects.create(
        conversation=conversation,
        whatsapp_message_id=f"out-{uuid.uuid4().hex}",
        direction="out",
        body=reply_body,
        timestamp=timezone.now(),
        is_escalation_trigger=escalate,
    )

    # Send to customer
    sent = send_message(tenant.whatsapp_phone_number_id, conversation.customer_phone, reply_body)
    if not sent:
        logger.error("Failed to send WhatsApp message to %s for tenant %s", conversation.customer_phone, tenant.slug)

    # Handle escalation
    if escalate and not conversation.is_escalated:
        conversation.is_escalated = True
        conversation.escalated_at = timezone.now()
        conversation.save(update_fields=["is_escalated", "escalated_at"])
        last_msg = incoming_message.body
        send_escalation_notification(tenant, conversation, last_msg)
        logger.info("Escalated conversation %s for tenant %s", conversation.pk, tenant.slug)
