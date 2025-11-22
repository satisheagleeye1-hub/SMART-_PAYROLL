from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Salary
from .serializers import SalarySerializer
from accounts.models import Employee


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_salary_api(request):
    """API endpoint for generating salary (Admin only)"""
    if not request.user.is_admin:
        return Response(
            {'error': 'Access denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    employee_id = request.data.get('employee')
    reference_date = request.data.get('reference_date')
    
    if not employee_id:
        return Response(
            {'error': 'Employee ID required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        employee = Employee.objects.get(emp_id=employee_id)
        
        if reference_date:
            from datetime import datetime
            ref_date = datetime.strptime(reference_date, '%Y-%m-%d').date()
        else:
            ref_date = timezone.now().date()
        
        start_date, end_date = Salary.get_salary_period(employee, ref_date)
        
        if not start_date or not end_date:
            return Response(
                {'error': 'Employee joining date is not set'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if salary already exists
        existing = Salary.objects.filter(
            employee=employee,
            start_date=start_date,
            end_date=end_date
        ).first()
        
        if existing:
            salary = existing
            salary.calculate_salary()
            salary.save()
        else:
            salary = Salary(
                employee=employee,
                start_date=start_date,
                end_date=end_date,
                basic_salary=employee.basic_salary
            )
            salary.calculate_salary()
            salary.save()
        
        serializer = SalarySerializer(salary)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def salary_details_api(request, salary_id):
    """API endpoint for getting salary details"""
    try:
        salary = Salary.objects.get(id=salary_id)
        
        # Check access
        if not request.user.is_admin and salary.employee != request.user:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = SalarySerializer(salary)
        return Response(serializer.data)
    except Salary.DoesNotExist:
        return Response(
            {'error': 'Salary not found'},
            status=status.HTTP_404_NOT_FOUND
        )

