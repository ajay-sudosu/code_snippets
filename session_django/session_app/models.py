from django.db import models

# Create your models here.


class Products(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    price = models.FloatField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image_url = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)


