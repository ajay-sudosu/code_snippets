from django.db import models

# Create your models here.

class Author(models.Model):  # user
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.first_name


class Book(models.Model):  # task
    name = models.CharField(max_length=100, null=True, blank=True)
    author = models.ManyToManyField(Author, related_name='books')

    def __str__(self):
        return self.name


class Address(models.Model):
    city = models.CharField(max_length=100, null=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.author.first_name
