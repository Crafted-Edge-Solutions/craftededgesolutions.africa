import hashlib
import hmac
import json
import logging
import uuid
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.utils import timezone

from subscriptions.models import InsightsSubscription, PaystackEventLog

logger = logging.getLogger(__name__)


class PaystackConfigurationError(RuntimeError):
    pass


class PaystackRequestError(RuntimeError):
    pass


def _api_request(path, payload=None, method="GET"):
    if not settings.PAYSTACK_SECRET_KEY:
        raise PaystackConfigurationError("PAYSTACK_SECRET_KEY is not configured.")

    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        f"{settings.PAYSTACK_BASE_URL}{path}",
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "CraftedEdgeSolutions/1.0 (+https://craftededgesolutions.africa)",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise PaystackRequestError(detail or str(exc)) from exc
    except URLError as exc:
        raise PaystackRequestError(str(exc)) from exc


def generate_reference():
    return f"CES-INS-{uuid.uuid4().hex[:12].upper()}"


def get_currency_amount(currency):
    """Return amount in smallest unit (kobo/pesewas/cents) for the given currency."""
    amounts = settings.PAYSTACK_CURRENCY_PRICES
    return amounts.get(currency, amounts["KES"])


def initialize_subscription_transaction(*, user, currency="KES", callback_url):
    """
    Initialize a Paystack transaction for the Insights subscription.
    Returns the authorization_url to redirect the user to Paystack.
    """
    reference = generate_reference()
    amount = get_currency_amount(currency)
    email = user.email

    payload = {
        "email": email,
        "amount": amount,
        "reference": reference,
        "callback_url": callback_url,
        "currency": currency,
        "metadata": {
            "user_id": user.pk,
            "product": "insights_subscription",
            "cancel_action": callback_url,
        },
    }
    # Attach plan code if configured (enables Paystack recurring billing)
    plan_code = settings.PAYSTACK_INSIGHTS_PLAN_CODE
    if plan_code:
        payload["plan"] = plan_code

    result = _api_request("/transaction/initialize", payload=payload, method="POST")
    data = result.get("data", {})

    # Record pending subscription
    subscription, _ = InsightsSubscription.objects.get_or_create(
        user=user,
        defaults={
            "email": email,
            "currency": currency,
            "amount": amount / 100,
            "reference": reference,
        },
    )
    if subscription.status not in (InsightsSubscription.STATUS_ACTIVE,):
        subscription.email = email
        subscription.currency = currency
        subscription.amount = amount / 100
        subscription.reference = reference
        subscription.status = InsightsSubscription.STATUS_PENDING
        subscription.save()

    return {
        "authorization_url": data.get("authorization_url", ""),
        "access_code": data.get("access_code", ""),
        "reference": reference,
    }


def verify_transaction(reference):
    return _api_request(f"/transaction/verify/{reference}")


def verify_webhook_signature(raw_body, received_signature):
    secret = settings.PAYSTACK_WEBHOOK_SECRET or settings.PAYSTACK_SECRET_KEY
    if not secret:
        return False
    expected = hmac.new(
        secret.encode("utf-8"),
        raw_body,
        hashlib.sha512,
    ).hexdigest()
    return hmac.compare_digest(expected, received_signature or "")


def handle_webhook_event(event_type, event_id, reference, data):
    """
    Process a verified Paystack webhook event.
    Updates InsightsSubscription and User.is_insights_member accordingly.
    """
    from accounts.models import User
    from newsletter.services import sync_subscriber_to_listmonk

    log, created = PaystackEventLog.objects.get_or_create(
        event_type=event_type,
        event_id=event_id,
        defaults={"reference": reference, "payload": data},
    )
    if not created and log.is_processed:
        logger.info("Skipping already-processed event %s / %s", event_type, event_id)
        return

    customer = data.get("customer", {})
    email = customer.get("email", "")
    customer_code = customer.get("customer_code", "")

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        logger.warning("Webhook event %s — no user found for %s", event_type, email)
        log.is_processed = True
        log.processed_at = timezone.now()
        log.save()
        return

    sub = InsightsSubscription.objects.filter(user=user).first()

    if event_type in ("charge.success", "subscription.create"):
        if sub:
            sub.status = InsightsSubscription.STATUS_ACTIVE
            sub.paystack_customer_code = customer_code
            sub.paid_at = timezone.now()
            subscription_code = data.get("subscription_code", "") or (
                data.get("subscription", {}).get("subscription_code", "")
            )
            if subscription_code:
                sub.paystack_subscription_code = subscription_code
            next_date_str = data.get("next_payment_date") or (
                data.get("subscription", {}).get("next_payment_date", "")
            )
            if next_date_str:
                try:
                    sub.next_payment_date = date.fromisoformat(next_date_str[:10])
                except ValueError:
                    pass
            sub.save()

        user.is_insights_member = True
        user.paystack_customer_code = customer_code
        user.save(update_fields=["is_insights_member", "paystack_customer_code"])

        sync_subscriber_to_listmonk(email=email, name=user.get_full_name() or email)

    elif event_type in ("subscription.disable", "subscription.not_renew"):
        if sub:
            sub.status = InsightsSubscription.STATUS_CANCELLED
            sub.save()
        user.is_insights_member = False
        user.save(update_fields=["is_insights_member"])

    log.is_processed = True
    log.processed_at = timezone.now()
    log.save()
