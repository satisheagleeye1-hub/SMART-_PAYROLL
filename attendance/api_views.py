from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, date
from .models import Attendance
from .serializers import AttendanceSerializer
from accounts.models import Employee


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clock_in_api(request):
    """API endpoint for clock-in"""
    today = timezone.now().date()
    
    # Check if already clocked in
    existing = Attendance.objects.filter(employee=request.user, date=today).first()
    
    if existing and existing.in_time:
        return Response(
            {'error': 'Already clocked in today'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if existing:
        attendance = existing
    else:
        attendance = Attendance(employee=request.user, date=today)
    
    attendance.in_time = timezone.now().time()
    attendance.save()
    
    serializer = AttendanceSerializer(attendance)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clock_out_api(request):
    """API endpoint for clock-out"""
    today = timezone.now().date()
    
    try:
        attendance = Attendance.objects.get(employee=request.user, date=today)
    except Attendance.DoesNotExist:
        return Response(
            {'error': 'Please clock in first'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not attendance.in_time:
        return Response(
            {'error': 'Please clock in first'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if attendance.out_time:
        return Response(
            {'error': 'Already clocked out today'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    attendance.out_time = timezone.now().time()
    attendance.save()
    
    serializer = AttendanceSerializer(attendance)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_list_api(request):
    """API endpoint for listing attendance"""
    attendances = Attendance.objects.all()
    
    # Filter by employee (for non-admin, only their own)
    if not request.user.is_admin:
        attendances = attendances.filter(employee=request.user)
    else:
        employee_id = request.GET.get('employee')
        if employee_id:
            attendances = attendances.filter(employee__emp_id=employee_id)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        attendances = attendances.filter(date__gte=date_from)
    if date_to:
        attendances = attendances.filter(date__lte=date_to)
    
    serializer = AttendanceSerializer(attendances.order_by('-date', '-in_time'), many=True)
    return Response(serializer.data)

