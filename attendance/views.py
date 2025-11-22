from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, date, timedelta
from .models import Attendance
from accounts.models import Employee


@login_required
def clock_in(request):
    """Employee clock-in view

    Supports:
    - POST: standard form submit with CSRF
    - GET with ?quick=1: perform quick clock-in (convenience for clients)
    """
    today = timezone.now().date()

    # Check if already clocked in today
    existing = Attendance.objects.filter(employee=request.user, date=today).first()

    if existing and existing.in_time:
        messages.warning(request, 'You have already clocked in today.')
        return redirect('attendance:my_attendance')

    # Quick clock-in via GET: /attendance/clock-in/?quick=1
    if request.method == 'GET' and request.GET.get('quick') == '1':
        if existing:
            attendance = existing
        else:
            attendance = Attendance(employee=request.user, date=today)

        # Use localtime to honor TIME_ZONE when USE_TZ is True
        attendance.in_time = timezone.localtime(timezone.now()).time()
        attendance.save()
        messages.success(request, f'Clocked in successfully at {attendance.in_time.strftime("%H:%M:%S")}')
        return redirect('attendance:my_attendance')

    if request.method == 'POST':
        if existing:
            attendance = existing
        else:
            attendance = Attendance(employee=request.user, date=today)

        attendance.in_time = timezone.localtime(timezone.now()).time()
        attendance.save()
        messages.success(request, f'Clocked in successfully at {attendance.in_time.strftime("%H:%M:%S")}')
        return redirect('attendance:my_attendance')

    return render(request, 'attendance/clock_in.html')


@login_required
def clock_out(request):
    """Employee clock-out view"""
    today = timezone.now().date()
    attendance = get_object_or_404(Attendance, employee=request.user, date=today)
    
    if not attendance.in_time:
        messages.error(request, 'Please clock in first.')
        return redirect('attendance:clock_in')
    
    if attendance.out_time:
        messages.warning(request, 'You have already clocked out today.')
        return redirect('attendance:my_attendance')
    
    if request.method == 'POST':
        attendance.out_time = timezone.localtime(timezone.now()).time()
        attendance.save()
        messages.success(request, f'Clocked out successfully at {attendance.out_time.strftime("%H:%M:%S")}')
        return redirect('attendance:my_attendance')
    
    return render(request, 'attendance/clock_out.html')


@login_required
def my_attendance(request):
    """Employee's own attendance history"""
    attendances = Attendance.objects.filter(employee=request.user).order_by('-date')[:30]
    
    # Today's attendance
    today = timezone.now().date()
    today_attendance = Attendance.objects.filter(employee=request.user, date=today).first()
    
    context = {
        'attendances': attendances,
        'today_attendance': today_attendance,
        'today': today,
    }
    return render(request, 'attendance/my_attendance.html', context)


@login_required
def all_attendance(request):
    """Admin view - All attendance records"""
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:employee_dashboard')
    
    attendances = Attendance.objects.all().order_by('-date', '-in_time')
    
    # Filters
    employee_id = request.GET.get('employee')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if employee_id:
        attendances = attendances.filter(employee__emp_id=employee_id)
    
    if date_from:
        attendances = attendances.filter(date__gte=date_from)
    
    if date_to:
        attendances = attendances.filter(date__lte=date_to)
    
    employees = Employee.objects.filter(status='Active').order_by('emp_id')
    
    context = {
        'attendances': attendances[:100],  # Limit to 100 for performance
        'employees': employees,
        'employee_id': employee_id,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'attendance/all_attendance.html', context)


@login_required
def edit_attendance(request, attendance_id):
    """Admin view - Edit attendance"""
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:employee_dashboard')
    
    attendance = get_object_or_404(Attendance, id=attendance_id)
    
    if request.method == 'POST':
        in_time_str = request.POST.get('in_time')
        out_time_str = request.POST.get('out_time')
        
        if in_time_str:
            attendance.in_time = datetime.strptime(in_time_str, '%H:%M').time()
        else:
            attendance.in_time = None
        
        if out_time_str:
            attendance.out_time = datetime.strptime(out_time_str, '%H:%M').time()
        else:
            attendance.out_time = None
        
        attendance.save()
        messages.success(request, 'Attendance updated successfully.')
        return redirect('attendance:all_attendance')
    
    return render(request, 'attendance/edit_attendance.html', {'attendance': attendance})


@login_required
def add_attendance(request):
    """Admin view - Manually add attendance"""
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:employee_dashboard')
    
    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        date_str = request.POST.get('date')
        in_time_str = request.POST.get('in_time')
        out_time_str = request.POST.get('out_time')
        
        try:
            employee = Employee.objects.get(emp_id=employee_id)
            att_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Check if attendance already exists
            attendance, created = Attendance.objects.get_or_create(
                employee=employee,
                date=att_date
            )
            
            if in_time_str:
                attendance.in_time = datetime.strptime(in_time_str, '%H:%M').time()
            if out_time_str:
                attendance.out_time = datetime.strptime(out_time_str, '%H:%M').time()
            
            attendance.save()
            messages.success(request, 'Attendance added successfully.')
            return redirect('attendance:all_attendance')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    employees = Employee.objects.filter(status='Active').order_by('emp_id')
    return render(request, 'attendance/add_attendance.html', {'employees': employees})
