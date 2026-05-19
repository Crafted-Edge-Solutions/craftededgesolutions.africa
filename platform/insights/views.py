import json
import os
import re

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from wagtail.rich_text import RichText

from .models import InsightsIndexPage, InsightsPostPage

VALID_CATEGORIES = {"architecture", "ai", "dx", "infrastructure", "product"}


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


@csrf_exempt
@require_POST
def create_draft_api(request):
    key = request.headers.get("X-Insights-Writer-Key", "")
    expected = os.environ.get("INSIGHTS_WRITER_KEY", "")
    if not expected or key != expected:
        return JsonResponse({"error": "unauthorized"}, status=401)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return JsonResponse({"error": f"invalid JSON: {e}"}, status=400)

    parent = InsightsIndexPage.objects.live().first()
    if not parent:
        return JsonResponse({"error": "No live InsightsIndexPage found"}, status=500)

    title = data.get("title") or "Untitled Insights Post"
    category = data.get("category", "architecture")
    if category not in VALID_CATEGORIES:
        category = "architecture"

    base_slug = _slugify(title)
    slug = base_slug
    counter = 1
    while InsightsPostPage.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    body = []
    if data.get("intro_html"):
        body.append(("paragraph", RichText(data["intro_html"])))
    if data.get("pullquote"):
        body.append(("pullquote", data["pullquote"]))
    for section in data.get("sections", []):
        if section.get("heading"):
            body.append(("heading", section["heading"]))
        if section.get("body_html"):
            body.append(("paragraph", RichText(section["body_html"])))
    if data.get("premium_html"):
        body.append(("premium_section", {"content": RichText(data["premium_html"])}))

    page = InsightsPostPage(
        title=title,
        slug=slug,
        category=category,
        summary=data.get("summary", ""),
        estimated_read_minutes=int(data.get("estimated_read_minutes", 7)),
        is_premium=True,
        body=body,
        live=False,
    )
    parent.add_child(instance=page)

    return JsonResponse({"ok": True, "id": page.pk, "slug": slug, "title": title})
