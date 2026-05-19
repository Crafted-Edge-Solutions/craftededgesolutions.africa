from django.urls import path

from . import views

urlpatterns = [
    path("", views.validator_home, name="validator_home"),
    path("submit/", views.validator_submit, name="validator_submit"),
    path("results/<uuid:uid>/", views.validator_results, name="validator_results"),
    path("upgrade/<uuid:uid>/", views.validator_upgrade, name="validator_upgrade"),
    path("callback/<uuid:uid>/", views.validator_callback, name="validator_callback"),
]
