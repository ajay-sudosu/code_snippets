from django.urls import path
from .views import *

urlpatterns = [
    path('employee_leaves', EmployeeLeaves.as_view(), name='employee_leaves'),
    path('employee_profile', EmployeeProfile.as_view(), name='employee_profile'),
]