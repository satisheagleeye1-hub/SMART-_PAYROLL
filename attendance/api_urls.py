from django.urls import path
from . import api_views

urlpatterns = [
    path('attendance/clock-in/', api_views.clock_in_api, name='api_clock_in'),
    path('attendance/clock-out/', api_views.clock_out_api, name='api_clock_out'),
    path('attendance/', api_views.attendance_list_api, name='api_attendance_list'),
]

