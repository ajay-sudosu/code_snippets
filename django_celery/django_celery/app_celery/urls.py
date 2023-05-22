from django.contrib import admin
from django.urls import path, include
from . import views
from .views import GetBooks, celery_add
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'books', GetBooks, basename='books')

urlpatterns = [
    path('', include(router.urls)),
    path('add', celery_add, name='add')
]
