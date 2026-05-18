from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Disable manifest storage in dev — avoid collectstatic requirement
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
