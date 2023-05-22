from django.contrib import admin
from custom_user_app import views
from django.urls import path

urlpatterns = [
    path('create-user/', views.CreateUser.as_view(), name='create-user'),
]
