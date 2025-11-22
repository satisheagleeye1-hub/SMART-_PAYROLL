from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from . import views
from . import employee_views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('employees/', employee_views.employee_list, name='employee_list'),
    path('employees/add/', employee_views.employee_add, name='employee_add'),
    path('employees/edit/<int:employee_id>/', employee_views.employee_edit, name='employee_edit'),
    path('employees/toggle/<int:employee_id>/', employee_views.employee_toggle_status, name='employee_toggle_status'),
    path('employees/password/<int:employee_id>/', employee_views.employee_change_password, name='employee_change_password'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
        success_url='/accounts/password-reset/done/'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/accounts/password-reset/complete/'
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
]
