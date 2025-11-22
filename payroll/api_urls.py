from django.urls import path
from . import api_views

urlpatterns = [
    path('salary/generate/', api_views.generate_salary_api, name='api_generate_salary'),
    path('salary/details/<int:salary_id>/', api_views.salary_details_api, name='api_salary_details'),
]

