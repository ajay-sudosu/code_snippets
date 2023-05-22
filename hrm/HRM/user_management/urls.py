from django.urls import path
from user_management.views import *
from . import views
urlpatterns = [

    path("home", views.home, name="home"),
    # path("employee_index", views.employee_index, name="home"),
    path('roles', Roles.as_view()),
    path('update_role/<id>', UpdateRole.as_view(), name="update_role"),
    path('delete_role/<id>', DeleteRole.as_view(), name="delete_role"),
    path('update_employee/<id>', UpdateEmployee.as_view(), name="update_employee"),
    path('delete_employee/<id>', DeleteEmployee.as_view(), name="delete_employee"),
    path('', LoginView.as_view(), name="login"),
    path('department', DepartmentView.as_view(), name="department"),
    path('update_department/<id>', UpdateDepartment.as_view(), name="update_department"),
    path('delete_department/<id>', DeleteDepartment.as_view(), name="delete_department"),
    path('employee', EmployeeView.as_view()),
    path('logout', views.logout_view),
]