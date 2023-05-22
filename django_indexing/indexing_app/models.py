from django.db import models

# Create your models here.

class Person(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    city = models.CharField(max_length=100, null=True, blank=True, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [models.Index(fields=['name'],)]


class Book(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name
