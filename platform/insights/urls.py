from django.urls import path

from . import views

urlpatterns = [
    path("api/create-draft/", views.create_draft_api, name="insights_create_draft"),
]
