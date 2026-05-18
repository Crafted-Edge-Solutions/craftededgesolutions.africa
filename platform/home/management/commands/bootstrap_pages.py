"""
Creates the initial Wagtail page tree:

  Root
  └── Home (/)
      ├── About (/about/)
      ├── Services (/services/)
      ├── Contact (/contact/)
      └── Insights (/insights/)
          └── (posts added via CMS)

Also configures the default Wagtail Site to point at the HomePage.
Safe to run multiple times — skips creation if pages already exist.
"""
from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from home.models import AboutPage, ContactPage, HomePage, ServicesPage, SolutionsIndexPage
from insights.models import InsightsIndexPage


class Command(BaseCommand):
    help = "Bootstrap initial CES page tree"

    def handle(self, *args, **options):
        root = Page.objects.filter(depth=1).first()
        if not root:
            self.stderr.write("No root page found. Run migrate first.")
            return

        # Home page — replace the default Wagtail welcome page if it exists
        if not HomePage.objects.exists():
            # Remove any existing placeholder page at depth=2 with slug 'home'
            existing = Page.objects.filter(depth=2, slug="home").exclude(
                id__in=HomePage.objects.values("id")
            ).first()
            if existing:
                existing.delete()
                self.stdout.write("Removed default Wagtail welcome page.")

            # Always reconcile root.numchild before adding — treebeard leaves it stale
            actual_count = Page.objects.filter(depth=2).count()
            Page.objects.filter(pk=root.pk).update(numchild=actual_count)
            root = Page.objects.get(pk=root.pk)

            home = HomePage(
                title="Crafted Edge Solutions",
                slug="home",
                hero_headline="Architecting\nResilient\nDigital\nEcosystems",
                hero_subheadline="Principal-led engineering studio. We build the infrastructure your business runs on.",
            )
            root.add_child(instance=home)
            self.stdout.write(f"Created HomePage id={home.pk}")
        else:
            home = HomePage.objects.first()
            self.stdout.write(f"HomePage already exists id={home.pk}")

        def add_child_if_missing(model, parent, **kwargs):
            if not model.objects.filter(slug=kwargs["slug"]).exists():
                page = model(**kwargs)
                parent.add_child(instance=page)
                self.stdout.write(f"Created {model.__name__} slug={kwargs['slug']}")
                return page
            obj = model.objects.get(slug=kwargs["slug"])
            self.stdout.write(f"{model.__name__} already exists slug={kwargs['slug']}")
            return obj

        add_child_if_missing(AboutPage, home, title="About", slug="about")
        add_child_if_missing(ServicesPage, home, title="Services", slug="services")
        add_child_if_missing(ContactPage, home, title="Contact", slug="contact")
        add_child_if_missing(SolutionsIndexPage, home, title="Work", slug="solutions")
        add_child_if_missing(
            InsightsIndexPage,
            home,
            title="Insights",
            slug="insights",
            intro="High-conviction technical reports and DX intelligence from the studio.",
        )

        # Wire up Wagtail Site
        site, created = Site.objects.get_or_create(
            hostname="localhost",
            defaults={
                "root_page": home,
                "is_default_site": True,
                "site_name": "Crafted Edge Solutions",
                "port": 8001,
            },
        )
        if not created:
            site.root_page = home
            site.save()
            self.stdout.write("Updated existing Site record.")
        else:
            self.stdout.write(f"Created Site record hostname={site.hostname}")

        self.stdout.write(self.style.SUCCESS("Bootstrap complete."))
