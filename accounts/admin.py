from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee, SystemSettings


@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    list_display = ('emp_id', 'username', 'email', 'first_name', 'last_name', 'role', 'status', 'join_date', 'basic_salary')
    list_filter = ('role', 'status', 'join_date')
    search_fields = ('emp_id', 'username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Employee Information', {
            'fields': ('emp_id', 'phone', 'role', 'join_date', 'training_date', 'basic_salary', 'incentive_rate', 'status')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Employee Information', {
            'fields': ('emp_id', 'phone', 'role', 'join_date', 'training_date', 'basic_salary', 'incentive_rate', 'status', 'email', 'first_name', 'last_name')
        }),
    )
    
    readonly_fields = ('emp_id', 'created_at')


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('office_start_time', 'late_cutoff_time', 'half_day_cutoff_time', 'penalty_per_minute', 'fixed_penalty', 'use_fixed_penalty', 'updated_at')
    
    def has_add_permission(self, request):
        # Only allow one settings instance
        return not SystemSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False

