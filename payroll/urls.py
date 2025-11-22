from django.urls import path
from . import views

app_name = 'payroll'

urlpatterns = [
    path('', views.salary_list, name='salary_list'),
    path('generate/', views.generate_salary, name='generate_salary'),
    path('generate/<str:employee_id>/', views.generate_salary, name='generate_salary_employee'),
    path('detail/<int:salary_id>/', views.salary_detail, name='salary_detail'),
    path('slip/<int:salary_id>/pdf/', views.generate_salary_slip_pdf, name='salary_slip_pdf'),
]

