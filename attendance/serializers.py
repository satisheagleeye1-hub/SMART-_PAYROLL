from rest_framework import serializers
from .models import Attendance
from accounts.models import Employee


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.emp_id', read_only=True)
    
    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'employee_id', 'employee_name', 'date', 'in_time', 
                  'out_time', 'late_minutes', 'half_day', 'penalty', 'is_present', 'working_hours']
        read_only_fields = ['late_minutes', 'penalty', 'half_day']

