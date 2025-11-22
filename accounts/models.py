from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import random
import string


class Employee(AbstractUser):
    """Custom User Model with Employee fields"""
    
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('User', 'User'),
    ]
    
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    
    emp_id = models.CharField(max_length=6, unique=True, editable=False)
    phone = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='User')
    join_date = models.DateField(null=True, blank=True)
    training_date = models.DateField(null=True, blank=True)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    incentive_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.emp_id:
            self.emp_id = self.generate_emp_id()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_emp_id():
        """Generate unique 6-digit Employee ID"""
        while True:
            emp_id = ''.join(random.choices(string.digits, k=6))
            if not Employee.objects.filter(emp_id=emp_id).exists():
                return emp_id
    
    def __str__(self):
        return f"{self.emp_id} - {self.get_full_name() or self.username}"
    
    @property
    def is_admin(self):
        return self.role == 'Admin'
    
    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'


class SystemSettings(models.Model):
    """System-wide settings for attendance rules"""
    office_start_time = models.TimeField(default='09:00:00', help_text="Office start time")
    late_cutoff_time = models.TimeField(default='09:15:00', help_text="Late cutoff time")
    half_day_cutoff_time = models.TimeField(default='12:00:00', help_text="Half-day cutoff time")
    penalty_per_minute = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Penalty per minute late")
    fixed_penalty = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Fixed penalty amount")
    use_fixed_penalty = models.BooleanField(default=False, help_text="Use fixed penalty instead of per-minute")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'
    
    def save(self, *args, **kwargs):
        # Ensure only one settings instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create system settings"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def __str__(self):
        return "System Settings"

