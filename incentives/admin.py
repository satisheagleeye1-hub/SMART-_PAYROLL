from django.contrib import admin
from .models import DailyCollection, Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile', 'location', 'area', 'mail_id', 'training_date', 'created_at')
    list_filter = ('location', 'area', 'training_date')
    search_fields = ('name', 'mobile', 'mail_id', 'location', 'area')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Person Information', {
            'fields': ('name', 'mobile', 'location', 'area', 'mail_id', 'training_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DailyCollection)
class DailyCollectionAdmin(admin.ModelAdmin):
    list_display = ('employee', 'person', 'date', 'office_type', 'amount_collected', 'payout_amount', 'incentive_earned', 'created_at')
    list_filter = ('date', 'office_type', 'employee__role')
    search_fields = ('employee__emp_id', 'employee__username', 'employee__first_name', 'employee__last_name', 'person__name', 'person__mobile')
    date_hierarchy = 'date'
    readonly_fields = ('incentive_earned', 'payout_amount', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Collection Information', {
            'fields': ('employee', 'person', 'date', 'office_type', 'amount_collected', 'payout_amount', 'incentive_earned')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

