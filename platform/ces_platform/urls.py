from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps import Sitemap as WagtailSitemap
from wagtail.documents import urls as wagtaildocs_urls

from core.views import careers, contact_api, llms_txt, pricing, robots_txt

wagtail_sitemaps = {"wagtail": WagtailSitemap}

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("accounts/", include("allauth.urls")),
    path("subscriptions/", include("subscriptions.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("pricing/", pricing, name="pricing"),
    path("careers/", careers, name="careers"),
    path("api/contact/", contact_api, name="contact_api"),
    path("newsletter/", include("newsletter.urls")),
    path("insights/", include("insights.urls")),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("llms.txt", llms_txt, name="llms_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": wagtail_sitemaps}, name="sitemap"),
    path("", include(wagtail_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
