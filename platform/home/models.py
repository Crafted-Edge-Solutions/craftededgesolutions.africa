from django.db import models
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from modelcluster.fields import ParentalKey


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


class SolutionsIndexPage(Page):
    intro = models.TextField(blank=True, default="Selected work from the studio.")

    max_count = 1
    parent_page_types = ["home.HomePage"]
    subpage_types = ["home.CaseStudyPage"]

    content_panels = Page.content_panels + [FieldPanel("intro")]

    def get_context(self, request):
        context = super().get_context(request)
        context["case_studies"] = CaseStudyPage.objects.child_of(self).live().order_by("-first_published_at")
        return context

    class Meta:
        verbose_name = "Solutions index"


OUTCOME_TAGS = [
    ("payment", "Payment integration"),
    ("ai", "AI / Automation"),
    ("platform", "Platform build"),
    ("infra", "Infrastructure"),
    ("mobile", "Mobile-first"),
    ("data", "Data & Analytics"),
]


class CaseStudyPage(Page):
    client_name = models.CharField(max_length=100)
    sector = models.CharField(max_length=100)
    outcome_tag = models.CharField(max_length=30, choices=OUTCOME_TAGS, default="platform")
    summary = models.TextField()
    challenge = RichTextField(blank=True)
    solution = RichTextField(blank=True)
    results = RichTextField(blank=True)
    stack = models.CharField(max_length=300, blank=True, help_text="Comma-separated stack items")
    timeline = models.CharField(max_length=60, blank=True)
    is_featured = models.BooleanField(default=False)

    parent_page_types = ["home.SolutionsIndexPage"]
    subpage_types = []

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("client_name"),
            FieldPanel("sector"),
            FieldPanel("outcome_tag"),
            FieldPanel("timeline"),
            FieldPanel("is_featured"),
        ], heading="Project details"),
        FieldPanel("summary"),
        FieldPanel("challenge"),
        FieldPanel("solution"),
        FieldPanel("results"),
        FieldPanel("stack"),
    ]

    def stack_items(self):
        return [s.strip() for s in self.stack.split(",") if s.strip()]

    class Meta:
        verbose_name = "Case study"


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
