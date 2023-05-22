# Django imports
from django.db import models
from django.conf import settings
# Module imports
from . import BaseModel

INTERVAL_CHOICES = (
    (20, "Yearly"),
    (15, "Monthly"),
)
class PricingPlan(BaseModel):
    name = models.CharField(max_length=255)
    stripe_plan_id = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    interval = models.PositiveSmallIntegerField(choices=INTERVAL_CHOICES, default=15)
    seats = models.PositiveBigIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "PricingPlan"
        verbose_name_plural = "PricingPlan"
        db_table = "pricingplan"
        ordering = ("-created_at",)

    