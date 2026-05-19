from django.urls import path

from . import views

urlpatterns = [
    # Meta webhook — single endpoint for all tenants
    path("webhook/", views.whatsapp_webhook, name="whatsapp_webhook"),

    # CES staff overview
    path("", views.tenant_list, name="agents_tenant_list"),

    # Per-tenant dashboard
    path("<slug:slug>/", views.dashboard, name="agents_dashboard"),
    path("<slug:slug>/knowledge/", views.knowledge_list, name="agents_knowledge"),
    path("<slug:slug>/knowledge/add/", views.knowledge_add, name="agents_knowledge_add"),
    path("<slug:slug>/knowledge/<int:entry_pk>/delete/", views.knowledge_delete, name="agents_knowledge_delete"),
    path("<slug:slug>/conversations/<int:convo_pk>/", views.conversation_detail, name="agents_conversation"),
]
