import json
import logging
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

META_API_URL = "https://graph.facebook.com/v19.0"


def _get_access_token():
    return os.environ.get("WHATSAPP_ACCESS_TOKEN", "")


def send_message(phone_number_id: str, to: str, body: str) -> bool:
    """Send a plain text WhatsApp message. Returns True on success."""
    token = _get_access_token()
    if not token:
        logger.error("WHATSAPP_ACCESS_TOKEN not configured")
        return False

    payload = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": body},
    }).encode()

    req = Request(
        f"{META_API_URL}/{phone_number_id}/messages",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return bool(data.get("messages"))
    except HTTPError as exc:
        logger.error("WhatsApp API error %s: %s", exc.code, exc.read().decode())
        return False
    except URLError as exc:
        logger.error("WhatsApp network error: %s", exc)
        return False


def mark_as_read(phone_number_id: str, message_id: str) -> None:
    """Send a read receipt for an incoming message."""
    token = _get_access_token()
    if not token:
        return

    payload = json.dumps({
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
    }).encode()

    req = Request(
        f"{META_API_URL}/{phone_number_id}/messages",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=10):
            pass
    except Exception as exc:
        logger.debug("mark_as_read error: %s", exc)


def send_escalation_notification(tenant, conversation, last_message_body: str) -> None:
    """Notify the tenant's escalation number when an escalation is triggered."""
    if not tenant.escalation_phone:
        return

    text = tenant.escalation_message_template.format(
        business_name=tenant.business_name,
        customer_phone=conversation.customer_phone,
        customer_name=conversation.customer_name or conversation.customer_phone,
        last_message=last_message_body[:200],
    )
    send_message(tenant.whatsapp_phone_number_id, tenant.escalation_phone, text)
