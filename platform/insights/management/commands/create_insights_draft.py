import json
import re

from django.core.management.base import BaseCommand, CommandError
from wagtail.rich_text import RichText

from insights.models import InsightsIndexPage, InsightsPostPage

VALID_CATEGORIES = {"architecture", "ai", "dx", "infrastructure", "product"}


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


class Command(BaseCommand):
    help = "Create an InsightsPostPage draft from a JSON file produced by insights-writer.py"

    def add_arguments(self, parser):
        parser.add_argument("json_path", help="Path to the insights draft JSON file")

    def handle(self, *args, **options):
        path = options["json_path"]
        try:
            with open(path) as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise CommandError(f"Cannot read draft file: {e}")

        parent = InsightsIndexPage.objects.live().first()
        if not parent:
            raise CommandError("No live InsightsIndexPage found — run bootstrap_pages first.")

        title = data.get("title") or "Untitled Insights Post"
        category = data.get("category", "architecture")
        if category not in VALID_CATEGORIES:
            category = "architecture"

        base_slug = slugify(title)
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
        self.stdout.write(f"id={page.pk} slug={slug} title={title!r}")
