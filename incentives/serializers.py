from rest_framework import serializers
from .models import DailyCollection
from accounts.models import Employee


class DailyCollectionSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.emp_id', read_only=True)
    
    class Meta:
        model = DailyCollection
        fields = ['id', 'employee', 'employee_id', 'employee_name', 'date', 
                  'amount_collected', 'incentive_earned', 'created_at']
        read_only_fields = ['incentive_earned']

