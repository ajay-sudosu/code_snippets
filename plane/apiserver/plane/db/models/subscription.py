# Django imports
from django.db import models
from django.conf import settings
# Module imports
from . import BaseModel

class Subscription(BaseModel):
    stripe_subscription_id = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    plan_id = models.ForeignKey("db.PricingPlan", on_delete=models.CASCADE)
    workspace_id = models.ForeignKey("db.Workspace", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        db_table = "subscriptions"
        ordering = ("-created_at",)