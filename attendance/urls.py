from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('clock-in/', views.clock_in, name='clock_in'),
    path('clock-out/', views.clock_out, name='clock_out'),
    path('my-attendance/', views.my_attendance, name='my_attendance'),
    path('all/', views.all_attendance, name='all_attendance'),
    path('edit/<int:attendance_id>/', views.edit_attendance, name='edit_attendance'),
    path('add/', views.add_attendance, name='add_attendance'),
]

