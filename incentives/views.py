from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from datetime import datetime
from decimal import Decimal
from .models import DailyCollection
from accounts.models import Employee


@login_required
def collection_list(request):
    """View all collections (Admin) or own collections (Employee)"""
    if request.user.is_admin:
        collections = DailyCollection.objects.all().order_by('-date', '-created_at')

        # Filters
        employee_id = request.GET.get('employee')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        if employee_id:
            collections = collections.filter(employee__emp_id=employee_id)
        
        if date_from:
            collections = collections.filter(date__gte=date_from)
        
        if date_to:
            collections = collections.filter(date__lte=date_to)
    else:
        collections = DailyCollection.objects.filter(employee=request.user).order_by('-date', '-created_at')

    # Calculate totals
    total_collected = collections.aggregate(Sum('amount_collected'))['amount_collected__sum'] or 0
    total_incentive = collections.aggregate(Sum('incentive_earned'))['incentive_earned__sum'] or 0
    
    employees = Employee.objects.filter(status='Active').order_by('emp_id') if request.user.is_admin else None
    
    context = {
        'collections': collections,  # show all matched collections
        'total_collected': total_collected,
        'total_incentive': total_incentive,
        'employees': employees,
        'employee_id': request.GET.get('employee'),
        'date_from': request.GET.get('date_from'),
        'date_to': request.GET.get('date_to'),
    }
    return render(request, 'incentives/collection_list.html', context)


@login_required
def add_collection(request):
    """Add daily collection (Admin only)"""
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:employee_dashboard')
    
    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        date_str = request.POST.get('date')
        amount = request.POST.get('amount_collected')
        
        try:
            employee = Employee.objects.get(emp_id=employee_id)
            coll_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            amount_decimal = Decimal(amount)
            
            if amount_decimal < 0:
                messages.error(request, 'Amount cannot be negative.')
                return redirect('incentives:add_collection')
            
            # Always create a new DailyCollection row so multiple collections per day are allowed
            DailyCollection.objects.create(
                employee=employee,
                date=coll_date,
                amount_collected=amount_decimal
            )
            messages.success(request, 'Collection added successfully.')

            return redirect('incentives:collection_list')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    employees = Employee.objects.filter(status='Active').order_by('emp_id')
    return render(request, 'incentives/add_collection.html', {'employees': employees})


@login_required
def edit_collection(request, collection_id):
    """Edit collection (Admin only)"""
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:employee_dashboard')
    
    collection = get_object_or_404(DailyCollection, id=collection_id)
    
    if request.method == 'POST':
        amount = request.POST.get('amount_collected')
        
        try:
            amount_decimal = Decimal(amount)
            if amount_decimal < 0:
                messages.error(request, 'Amount cannot be negative.')
                return redirect('incentives:edit_collection', collection_id=collection_id)
            
            collection.amount_collected = amount_decimal
            collection.save()
            messages.success(request, 'Collection updated successfully.')
            return redirect('incentives:collection_list')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'incentives/edit_collection.html', {'collection': collection})


@login_required
def delete_collection(request, collection_id):
    """Delete collection (Admin only)"""
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:employee_dashboard')
    
    collection = get_object_or_404(DailyCollection, id=collection_id)
    
    if request.method == 'POST':
        collection.delete()
        messages.success(request, 'Collection deleted successfully.')
        return redirect('incentives:collection_list')
    
    return render(request, 'incentives/delete_collection.html', {'collection': collection})


# New view: incentive_report
from django.db.models import F
from django.db.models.functions import TruncDate, TruncMonth


@login_required
def incentive_report(request):
    """Report: total incentive per employee, day-wise or month-wise (Admin only)."""
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:employee_dashboard')

    # Filters
    mode = request.GET.get('mode', 'day')  # 'day' or 'month'
    employee_id = request.GET.get('employee')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    qs = DailyCollection.objects.all()
    if employee_id:
        qs = qs.filter(employee__emp_id=employee_id)
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)

    if mode == 'month':
        # Group by employee and month
        rows = (qs.annotate(period=TruncMonth('date'))
                .values('employee__emp_id', 'employee__first_name', 'employee__last_name', 'period')
                .annotate(total_collected=Sum('amount_collected'), total_incentive=Sum('incentive_earned'))
                .order_by('employee__emp_id', '-period'))
    else:
        # Group by employee and exact date
        rows = (qs.annotate(period=TruncDate('date'))
                .values('employee__emp_id', 'employee__first_name', 'employee__last_name', 'period')
                .annotate(total_collected=Sum('amount_collected'), total_incentive=Sum('incentive_earned'))
                .order_by('employee__emp_id', '-period'))

    employees = Employee.objects.filter(status='Active').order_by('emp_id')

    # Totals across the result set
    grand_collected = sum([r['total_collected'] or 0 for r in rows])
    grand_incentive = sum([r['total_incentive'] or 0 for r in rows])

    context = {
        'rows': rows,
        'employees': employees,
        'employee_id': employee_id,
        'date_from': date_from,
        'date_to': date_to,
        'mode': mode,
        'grand_collected': grand_collected,
        'grand_incentive': grand_incentive,
    }

    return render(request, 'incentives/incentive_report.html', context)
