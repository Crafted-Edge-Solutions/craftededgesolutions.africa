from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class HomePage(Page):
    """Root page for craftededgesolutions.africa"""
    hero_headline = models.CharField(
        max_length=120,
        default="Architecting\nResilient\nDigital\nEcosystems",
    )
    hero_subheadline = models.CharField(
        max_length=200,
        default="Principal-led engineering studio. We build the infrastructure your business runs on.",
    )
    hero_cta_label = models.CharField(max_length=60, default="See Our Work")
    hero_cta_url = models.CharField(max_length=200, default="/services/")

    intro_body = RichTextField(
        blank=True,
        features=["bold", "italic", "ul", "link"],
        help_text="Short intro below the hero stats.",
    )

    max_count = 1
    parent_page_types = ["wagtailcore.Page"]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("hero_headline"),
            FieldPanel("hero_subheadline"),
            FieldPanel("hero_cta_label"),
            FieldPanel("hero_cta_url"),
        ], heading="Hero"),
        FieldPanel("intro_body"),
    ]

    class Meta:
        verbose_name = "Home page"


class AboutPage(Page):
    body = RichTextField(blank=True)

    max_count = 1
    parent_page_types = ["home.HomePage"]

    content_panels = Page.content_panels + [FieldPanel("body")]


class ServicesPage(Page):
    intro = models.TextField(blank=True)
    body = RichTextField(blank=True)

    max_count = 1
    parent_page_types = ["home.HomePage"]

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
    ]


class ContactPage(Page):
    intro = models.TextField(
        blank=True,
        default="We take on 5 high-impact partnerships at a time. If you're building something that matters, let's talk.",
    )
    email = models.EmailField(default="hello@craftededgesolutions.africa")
    calendly_url = models.URLField(blank=True)

    max_count = 1
    parent_page_types = ["home.HomePage"]

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("email"),
        FieldPanel("calendly_url"),
    ]
