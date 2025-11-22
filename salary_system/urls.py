"""
URL configuration for salary_system project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dashboard.root_view import root_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('attendance/', include('attendance.urls')),
    path('payroll/', include('payroll.urls')),
    path('incentives/', include('incentives.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('api/', include('attendance.api_urls')),
    path('api/', include('payroll.api_urls')),
    path('api/', include('incentives.api_urls')),
    path('', root_view, name='root'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

