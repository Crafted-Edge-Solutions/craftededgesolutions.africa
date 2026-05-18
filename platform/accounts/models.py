from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model. is_insights_member is set to True once a paid
    Paystack subscription is confirmed via webhook.
    """
    is_insights_member = models.BooleanField(default=False)
    paystack_customer_code = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return self.email or self.username
