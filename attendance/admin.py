from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'in_time', 'out_time', 'late_minutes', 'half_day', 'penalty', 'is_present')
    list_filter = ('date', 'half_day', 'employee__role')
    search_fields = ('employee__emp_id', 'employee__username', 'employee__first_name', 'employee__last_name')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('employee', 'date')
        }),
        ('Attendance Details', {
            'fields': ('in_time', 'out_time', 'late_minutes', 'half_day', 'penalty')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

