from django.db import models
from django.urls import reverse


# Create your models here.
class Hello(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)


    def get_absolute_url(self):
        return reverse('helloDetail', args=[str(self.id)])
        # return reverse('helloDetail',  kwargs={'pk': self.pk})

    def __str__(self):
        return self.name
