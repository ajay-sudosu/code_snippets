from django.contrib import admin
from django.urls import path
from settings_app import views

urlpatterns = [
    path('hello/', views.helloView, name='helloView'),
    path('detail_test/<int:id>', views.helloDetail, name='detail_test'),
    path('detail/<int:pk>', views.HelloDetailView.as_view(), name='helloDetail'),
]
