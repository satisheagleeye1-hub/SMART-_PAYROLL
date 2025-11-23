from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.utils.safestring import mark_safe
import json
from datetime import datetime, date, timedelta
from decimal import Decimal
from accounts.models import Employee
from attendance.models import Attendance
from incentives.models import DailyCollection
from payroll.models import Salary


@login_required
def admin_dashboard(request):
    """Admin dashboard with comprehensive metrics"""
    if not request.user.is_admin:
        return redirect('dashboard:employee_dashboard')
    
    today = timezone.now().date()
    current_month_start = date(today.year, today.month, 1)
    
    # Today's attendance stats
    today_attendances = Attendance.objects.filter(date=today)
    present_count = today_attendances.filter(in_time__isnull=False).count()
    absent_count = Employee.objects.filter(status='Active').count() - present_count
    
    # Today's collections
    today_collections = DailyCollection.objects.filter(date=today)
    daily_collections = today_collections.aggregate(Sum('amount_collected'))['amount_collected__sum'] or Decimal('0.00')
    daily_payout = today_collections.aggregate(Sum('payout_amount'))['payout_amount__sum'] or Decimal('0.00')
    today_incentive = today_collections.aggregate(Sum('incentive_earned'))['incentive_earned__sum'] or Decimal('0.00')
    
    # First office and second office payouts for today
    first_office_today = today_collections.filter(office_type='first').aggregate(Sum('payout_amount'))['payout_amount__sum'] or Decimal('0.00')
    second_office_today = today_collections.filter(office_type='second').aggregate(Sum('payout_amount'))['payout_amount__sum'] or Decimal('0.00')
    
    # Monthly collections
    month_collections = DailyCollection.objects.filter(date__gte=current_month_start, date__lte=today)
    monthly_collections = month_collections.aggregate(Sum('amount_collected'))['amount_collected__sum'] or Decimal('0.00')
    monthly_payout = month_collections.aggregate(Sum('payout_amount'))['payout_amount__sum'] or Decimal('0.00')
    monthly_incentive = month_collections.aggregate(Sum('incentive_earned'))['incentive_earned__sum'] or Decimal('0.00')

    
    # Today's attendance list
    today_attendance_list = today_attendances.filter(in_time__isnull=False).order_by('-in_time')[:10]
    
    # Recent collections
    recent_collections = DailyCollection.objects.order_by('-date')[:10]
    
    # Low attendance alerts (employees with < 20 days attendance this month)
    month_attendances = Attendance.objects.filter(
        date__gte=current_month_start,
        date__lte=today
    ).values('employee').annotate(
        present_days=Count('id', filter=Q(in_time__isnull=False))
    ).filter(present_days__lt=20)
    
    low_attendance_employees = []
    for att in month_attendances:
        employee = Employee.objects.get(id=att['employee'])
        low_attendance_employees.append({
            'employee': employee,
            'present_days': att['present_days']
        })
    
    # Chart data - Monthly attendance (last 6 months)
    chart_months = []
    chart_attendance = []
    for i in range(5, -1, -1):
        month_date = today - timedelta(days=30*i)
        month_start = date(month_date.year, month_date.month, 1)
        if month_date.month == 12:
            month_end = date(month_date.year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(month_date.year, month_date.month + 1, 1) - timedelta(days=1)
        
        month_attendance = Attendance.objects.filter(
            date__gte=month_start,
            date__lte=month_end,
            in_time__isnull=False
        ).count()
        
        chart_months.append(month_start.strftime('%b %Y'))
        chart_attendance.append(month_attendance)
    
    # Chart data - Daily collection (last 30 days)
    chart_dates = []
    chart_collections = []
    for i in range(29, -1, -1):
        day_date = today - timedelta(days=i)
        day_collection = DailyCollection.objects.filter(date=day_date).aggregate(
            Sum('amount_collected')
        )['amount_collected__sum'] or 0
        
        chart_dates.append(day_date.strftime('%d/%m'))
        chart_collections.append(float(day_collection))
    
    # Chart data - Salary distribution (pie chart)
    salary_ranges = [
        {'label': '0-20k', 'count': 0},
        {'label': '20k-40k', 'count': 0},
        {'label': '40k-60k', 'count': 0},
        {'label': '60k+', 'count': 0},
    ]
    
    active_employees = Employee.objects.filter(status='Active')
    for emp in active_employees:
        salary = float(emp.basic_salary)
        if salary < 20000:
            salary_ranges[0]['count'] += 1
        elif salary < 40000:
            salary_ranges[1]['count'] += 1
        elif salary < 60000:
            salary_ranges[2]['count'] += 1
        else:
            salary_ranges[3]['count'] += 1
    
    context = {
        'present_count': present_count,
        'absent_count': absent_count,
        'daily_collections': daily_collections,
        'daily_payout': daily_payout,
        'monthly_collections': monthly_collections,
        'monthly_payout': monthly_payout,
        'today_incentive': today_incentive,
        'monthly_incentive': monthly_incentive,
        'first_office_payout': first_office_today,
        'second_office_payout': second_office_today,
        'today_attendance_list': today_attendance_list,
        'recent_collections': recent_collections,
        'low_attendance_employees': low_attendance_employees[:5],
        'chart_months': mark_safe(json.dumps(chart_months)),
        'chart_attendance': mark_safe(json.dumps(chart_attendance)),
        'chart_dates': mark_safe(json.dumps(chart_dates)),
        'chart_collections': mark_safe(json.dumps(chart_collections)),
        'salary_ranges': salary_ranges,
        'today': today,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def employee_dashboard(request):
    """Employee dashboard with simplified view"""
    today = timezone.now().date()
    current_month_start = date(today.year, today.month, 1)
    
    # Today's attendance
    today_attendance = Attendance.objects.filter(employee=request.user, date=today).first()
    
    # Month summary
    month_attendances = Attendance.objects.filter(
        employee=request.user,
        date__gte=current_month_start,
        date__lte=today
    )
    total_attendance = month_attendances.filter(in_time__isnull=False).count()
    
    # Month collections
    month_collections = DailyCollection.objects.filter(
        employee=request.user,
        date__gte=current_month_start,
        date__lte=today
    )
    total_collection = month_collections.aggregate(Sum('amount_collected'))['amount_collected__sum'] or 0
    total_incentive = month_collections.aggregate(Sum('incentive_earned'))['incentive_earned__sum'] or 0
    
    # Month penalties
    total_penalty = month_attendances.aggregate(Sum('penalty'))['penalty__sum'] or 0
    
    # Latest salary
    latest_salary = Salary.objects.filter(employee=request.user).order_by('-end_date').first()
    
    context = {
        'today_attendance': today_attendance,
        'today': today,
        'total_attendance': total_attendance,
        'total_collection': total_collection,
        'total_incentive': total_incentive,
        'total_penalty': total_penalty,
        'latest_salary': latest_salary,
    }
    return render(request, 'dashboard/employee_dashboard.html', context)
