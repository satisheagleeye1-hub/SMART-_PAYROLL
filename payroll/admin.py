from django.contrib import admin
from .models import Salary


@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'start_date', 'end_date', 'basic_salary', 'total_incentive', 
                    'total_penalty', 'net_salary', 'total_present_days', 'created_at')
    list_filter = ('start_date', 'end_date', 'employee__role')
    search_fields = ('employee__emp_id', 'employee__username', 'employee__first_name', 'employee__last_name')
    date_hierarchy = 'start_date'
    readonly_fields = ('breakdown', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('employee',)
        }),
        ('Salary Period', {
            'fields': ('start_date', 'end_date')
        }),
        ('Salary Details', {
            'fields': ('basic_salary', 'total_incentive', 'total_penalty', 'half_day_cuts',
                      'total_working_days', 'total_present_days', 'net_salary')
        }),
        ('Breakdown', {
            'fields': ('breakdown',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

