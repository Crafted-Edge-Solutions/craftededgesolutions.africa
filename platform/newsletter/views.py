import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import NewsletterSubscriber
from .services import sync_subscriber_to_listmonk


@csrf_exempt
@require_POST
def signup(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        data = {}

    email = (data.get("email") or "").strip().lower()
    name = (data.get("name") or "").strip()

    if not email or "@" not in email:
        return JsonResponse({"ok": False, "error": "Valid email required."}, status=400)

    obj, created = NewsletterSubscriber.objects.get_or_create(
        email=email,
        defaults={"name": name},
    )
    if not created and not obj.is_active:
        obj.is_active = True
        obj.save(update_fields=["is_active"])

    sync_subscriber_to_listmonk(email=email, name=name)

    return JsonResponse({"ok": True, "created": created})
