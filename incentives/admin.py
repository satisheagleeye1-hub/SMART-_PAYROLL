from django.contrib import admin
from .models import DailyCollection


@admin.register(DailyCollection)
class DailyCollectionAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'amount_collected', 'incentive_earned', 'created_at')
    list_filter = ('date', 'employee__role')
    search_fields = ('employee__emp_id', 'employee__username', 'employee__first_name', 'employee__last_name')
    date_hierarchy = 'date'
    readonly_fields = ('incentive_earned', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Collection Information', {
            'fields': ('employee', 'date', 'amount_collected', 'incentive_earned')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

