import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .services import (
    PaystackConfigurationError,
    PaystackRequestError,
    handle_webhook_event,
    initialize_subscription_transaction,
    verify_transaction,
    verify_webhook_signature,
)

logger = logging.getLogger(__name__)


@login_required
def subscribe(request):
    if request.user.is_insights_member:
        messages.info(request, "You already have an active Insights membership.")
        return redirect("/insights/")

    currency = request.GET.get("currency", "KES").upper()
    callback_url = request.build_absolute_uri("/subscriptions/callback/")

    try:
        result = initialize_subscription_transaction(
            user=request.user,
            currency=currency,
            callback_url=callback_url,
        )
    except PaystackConfigurationError:
        messages.error(request, "Payment is not configured yet. Please contact us.")
        return redirect("/insights/")
    except PaystackRequestError as exc:
        logger.error("Paystack error during subscribe: %s", exc)
        messages.error(request, "Could not initiate payment. Please try again.")
        return redirect("/insights/")

    return redirect(result["authorization_url"])


@login_required
def subscribe_callback(request):
    reference = request.GET.get("reference", "")
    if not reference:
        messages.error(request, "Payment reference missing.")
        return redirect("/insights/")

    try:
        result = verify_transaction(reference)
    except (PaystackConfigurationError, PaystackRequestError) as exc:
        logger.error("Verify error: %s", exc)
        messages.error(request, "Could not verify payment. Please contact us.")
        return redirect("/insights/")

    data = result.get("data", {})
    status = data.get("status", "")

    if status == "success":
        handle_webhook_event(
            event_type="charge.success",
            event_id=data.get("id", ""),
            reference=reference,
            data=data,
        )
        messages.success(request, "Welcome to Insights! Your membership is now active.")
        return redirect("/insights/")
    else:
        messages.error(request, f"Payment was not successful (status: {status}). Please try again.")
        return redirect("/insights/")


@csrf_exempt
@require_POST
def paystack_webhook(request):
    signature = request.headers.get("X-Paystack-Signature", "")
    if not verify_webhook_signature(request.body, signature):
        return HttpResponseBadRequest("Invalid signature")

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    event_type = payload.get("event", "")
    data = payload.get("data", {})
    event_id = str(data.get("id", ""))
    reference = data.get("reference", "") or data.get("subscription_code", "")

    logger.info("Paystack webhook received: %s / %s", event_type, event_id)

    try:
        handle_webhook_event(
            event_type=event_type,
            event_id=event_id,
            reference=reference,
            data=data,
        )
    except Exception as exc:
        logger.exception("Error handling webhook event %s: %s", event_type, exc)
        # Return 200 to prevent Paystack retries on non-transient errors
        return HttpResponse("error logged", status=200)

    return HttpResponse("ok", status=200)
