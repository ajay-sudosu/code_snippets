from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializer import *
from .models import Book, Author, Address
from django.forms.models import model_to_dict
from django.db.models import Count
from django.db.models import Avg
from pathlib import Path
from rest_framework.viewsets import ModelViewSet
from django_celery.tasks import add
from rest_framework.decorators import api_view

# Create your views here.

@api_view(['GET'])
def celery_add(request):
    task = add.delay(1, 0)
    return Response({"msg": "The sum is done."})

class GetBooks(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
