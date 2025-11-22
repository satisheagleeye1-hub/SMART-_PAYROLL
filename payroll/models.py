from django.db import models
from django.utils import timezone
from accounts.models import Employee
from decimal import Decimal
from datetime import date, timedelta
import json


class Salary(models.Model):
    """Salary records based on joining date cycle"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salaries')
    start_date = models.DateField()
    end_date = models.DateField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_incentive = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_penalty = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    half_day_cuts = models.IntegerField(default=0)
    total_working_days = models.IntegerField(default=0)
    total_present_days = models.IntegerField(default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    breakdown = models.JSONField(default=dict, help_text="Detailed salary breakdown")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-end_date']
        verbose_name_plural = 'Salaries'
    
    def __str__(self):
        return f"{self.employee.emp_id} - {self.start_date} to {self.end_date} - ₹{self.net_salary}"
    
    def calculate_salary(self):
        """Calculate salary based on attendance, collections, and penalties"""
        from attendance.models import Attendance
        from incentives.models import DailyCollection
        from datetime import timedelta
        
        # Get all attendances in the period
        attendances = Attendance.objects.filter(
            employee=self.employee,
            date__gte=self.start_date,
            date__lte=self.end_date
        )
        
        # Get all collections in the period
        collections = DailyCollection.objects.filter(
            employee=self.employee,
            date__gte=self.start_date,
            date__lte=self.end_date
        )
        
        # Calculate totals
        self.total_present_days = attendances.filter(in_time__isnull=False).count()
        self.total_working_days = (self.end_date - self.start_date).days + 1
        self.half_day_cuts = attendances.filter(half_day=True).count()
        
        # Calculate total penalty from attendance
        self.total_penalty = attendances.aggregate(
            total=models.Sum('penalty')
        )['total'] or Decimal('0.00')
        
        # Calculate total incentive from collections
        self.total_incentive = collections.aggregate(
            total=models.Sum('incentive_earned')
        )['total'] or Decimal('0.00')
        
        # Calculate half-day salary cut
        # Assuming half-day means 50% of daily salary
        daily_salary = self.basic_salary / 30  # Approximate daily salary
        half_day_cut_amount = (self.half_day_cuts * daily_salary) / 2
        self.total_penalty += half_day_cut_amount
        
        # Calculate net salary
        self.net_salary = self.basic_salary - self.total_penalty + self.total_incentive
        
        # Ensure net salary is not negative
        if self.net_salary < 0:
            self.net_salary = Decimal('0.00')
        
        # Create breakdown
        self.breakdown = {
            'basic_salary': float(self.basic_salary),
            'total_incentive': float(self.total_incentive),
            'total_penalty': float(self.total_penalty),
            'half_day_cuts': self.half_day_cuts,
            'half_day_cut_amount': float(half_day_cut_amount),
            'total_working_days': self.total_working_days,
            'total_present_days': self.total_present_days,
            'net_salary': float(self.net_salary),
        }
    
    def save(self, *args, **kwargs):
        if not self.breakdown:
            self.calculate_salary()
        super().save(*args, **kwargs)
    
    @staticmethod
    def get_salary_period(employee, reference_date=None):
        """Get salary period based on joining date"""
        if reference_date is None:
            reference_date = timezone.now().date()
        
        if not employee.join_date:
            return None, None
        
        join_date = employee.join_date
        
        # Calculate months since joining
        months_since_joining = (reference_date.year - join_date.year) * 12 + (reference_date.month - join_date.month)
        
        # Calculate start date of current cycle
        start_year = join_date.year
        start_month = join_date.month + months_since_joining
        
        # Handle month overflow
        while start_month > 12:
            start_month -= 12
            start_year += 1
        
        start_date = date(start_year, start_month, join_date.day)
        
        # Calculate end date (one month from start)
        end_year = start_year
        end_month = start_month + 1
        if end_month > 12:
            end_month = 1
            end_year += 1
        
        # Get last day of end month
        if end_month == 12:
            next_month = 1
            next_year = end_year + 1
        else:
            next_month = end_month + 1
            next_year = end_year
        
        end_date = date(next_year, next_month, 1) - timedelta(days=1)
        
        # If reference_date is before end_date, adjust
        if reference_date < end_date:
            end_date = reference_date
        
        return start_date, end_date

