from rest_framework import serializers
from .models import Salary
from accounts.models import Employee


class SalarySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.emp_id', read_only=True)
    
    class Meta:
        model = Salary
        fields = ['id', 'employee', 'employee_id', 'employee_name', 'start_date', 'end_date',
                  'basic_salary', 'total_incentive', 'total_penalty', 'half_day_cuts',
                  'total_working_days', 'total_present_days', 'net_salary', 'breakdown', 'created_at']

