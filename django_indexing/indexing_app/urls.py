from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('fetch_person/', views.fetch_person, name='fetch_person'),
    path('add_person/', views.add_person, name='add_person'),
    path('add_book/', views.add_book, name='add_book'),
    path('get_book/', views.get_book, name='get_book'),
    path('update_data/', views.update_data, name='update_data'),
    path('random_data/', views.random_data_post, name='random_data'),

]
