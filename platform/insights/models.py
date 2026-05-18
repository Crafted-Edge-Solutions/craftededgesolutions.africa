from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.blocks import (
    CharBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
    TextBlock,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtail.snippets.models import register_snippet


class GatedBlock(StructBlock):
    """
    A StreamField block whose content is only rendered for active Insights members.
    Editors drop this block around premium sections — template checks request.user.is_insights_member.
    """
    content = RichTextBlock(features=["bold", "italic", "ul", "ol", "link", "h2", "h3"])

    class Meta:
        icon = "lock"
        label = "Premium (gated) content"
        template = "insights/blocks/gated_block.html"


class InsightsStreamBlock(StreamBlock):
    heading = CharBlock(icon="title", form_classname="full title")
    paragraph = RichTextBlock(features=["bold", "italic", "ul", "ol", "link", "h2", "h3"])
    image = ImageChooserBlock()
    pullquote = TextBlock(icon="openquote")
    premium_section = GatedBlock()


class InsightsIndexPage(Page):
    """Hub page listing all Insights reports."""
    intro = models.TextField(
        blank=True,
        default="High-conviction technical reports and DX intelligence from the studio.",
    )
    subscription_pitch = models.CharField(
        max_length=200,
        blank=True,
        default="Full reports for Insights members — KES 499 / USD 4.99 per month.",
    )

    max_count = 1
    parent_page_types = ["home.HomePage"]
    subpage_types = ["insights.InsightsPostPage"]

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("subscription_pitch"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["posts"] = (
            InsightsPostPage.objects.live()
            .order_by("-first_published_at")
        )
        return context

    class Meta:
        verbose_name = "Insights index"


class InsightsPostPage(Page):
    """A single Insights report."""
    CATEGORY_CHOICES = [
        ("architecture", "Architecture"),
        ("ai", "AI & ML"),
        ("dx", "Developer Experience"),
        ("infrastructure", "Infrastructure"),
        ("product", "Product Engineering"),
    ]

    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default="architecture")
    summary = models.TextField(
        blank=True,
        help_text="Short excerpt shown on the index and to non-members.",
    )
    estimated_read_minutes = models.PositiveSmallIntegerField(default=5)
    is_premium = models.BooleanField(
        default=True,
        help_text="If checked, non-members see only the summary and a paywall.",
    )
    body = StreamField(InsightsStreamBlock(), use_json_field=True, blank=True)

    parent_page_types = ["insights.InsightsIndexPage"]
    subpage_types = []

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("category"),
            FieldPanel("estimated_read_minutes"),
            FieldPanel("is_premium"),
            FieldPanel("summary"),
        ], heading="Post metadata"),
        FieldPanel("body"),
    ]

    def user_can_read(self, user):
        if not self.is_premium:
            return True
        return user.is_authenticated and getattr(user, "is_insights_member", False)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["user_can_read"] = self.user_can_read(request.user)
        return context

    class Meta:
        verbose_name = "Insights post"
        verbose_name_plural = "Insights posts"
