from django.db import models
from django.utils import timezone
from accounts.models import Employee, SystemSettings
from datetime import datetime, timedelta


class Attendance(models.Model):
    """Employee attendance records"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    in_time = models.TimeField(null=True, blank=True)
    out_time = models.TimeField(null=True, blank=True)
    late_minutes = models.IntegerField(default=0)
    half_day = models.BooleanField(default=False)
    penalty = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['employee', 'date']
        ordering = ['-date', '-in_time']
        verbose_name_plural = 'Attendances'
    
    def __str__(self):
        return f"{self.employee.emp_id} - {self.date}"
    
    def calculate_late_and_penalty(self):
        """Calculate late minutes and penalty based on system settings"""
        if not self.in_time:
            return
        
        settings = SystemSettings.get_settings()
        office_start = datetime.combine(self.date, settings.office_start_time)
        in_datetime = datetime.combine(self.date, self.in_time)
        
        # Check if late
        if in_datetime > datetime.combine(self.date, settings.late_cutoff_time):
            late_delta = in_datetime - datetime.combine(self.date, settings.late_cutoff_time)
            self.late_minutes = int(late_delta.total_seconds() / 60)
            
            # Calculate penalty
            if settings.use_fixed_penalty:
                self.penalty = settings.fixed_penalty
            else:
                self.penalty = self.late_minutes * settings.penalty_per_minute
        else:
            self.late_minutes = 0
            self.penalty = 0.00
        
        # Check if half-day
        if in_datetime > datetime.combine(self.date, settings.half_day_cutoff_time):
            self.half_day = True
        else:
            self.half_day = False
    
    def save(self, *args, **kwargs):
        if self.in_time:
            self.calculate_late_and_penalty()
        super().save(*args, **kwargs)
    
    @property
    def is_present(self):
        return self.in_time is not None
    
    @property
    def is_absent(self):
        return self.in_time is None
    
    @property
    def working_hours(self):
        if self.in_time and self.out_time:
            in_dt = datetime.combine(self.date, self.in_time)
            out_dt = datetime.combine(self.date, self.out_time)
            delta = out_dt - in_dt
            return delta.total_seconds() / 3600
        return 0

