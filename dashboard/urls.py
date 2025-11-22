from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('employee/', views.employee_dashboard, name='employee_dashboard'),
]

