from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Employee
from .forms import EmployeeForm


@login_required
def employee_list(request):
    """List all employees (Admin only)"""
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:employee_dashboard')
    
    employees = Employee.objects.all().order_by('-created_at')
    
    # Search/Filter
    search = request.GET.get('search')
    role_filter = request.GET.get('role')
    status_filter = request.GET.get('status')
    
    if search:
        employees = employees.filter(
            Q(emp_id__icontains=search) |
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    if role_filter:
        employees = employees.filter(role=role_filter)
    
    if status_filter:
        employees = employees.filter(status=status_filter)
    
    context = {
        'employees': employees,
        'search': search,
        'role_filter': role_filter,
        'status_filter': status_filter,
    }
    return render(request, 'accounts/employee_list.html', context)


@login_required
def employee_add(request):
    """Add new employee (Admin only)"""
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:employee_dashboard')
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Employee {employee.emp_id} added successfully.')
            return redirect('accounts:employee_list')
    else:
        form = EmployeeForm()
    
    return render(request, 'accounts/employee_form.html', {'form': form, 'action': 'Add'})


@login_required
def employee_edit(request, employee_id):
    """Edit employee (Admin only)"""
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:employee_dashboard')
    
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Employee {employee.emp_id} updated successfully.')
            return redirect('accounts:employee_list')
    else:
        form = EmployeeForm(instance=employee)
    
    return render(request, 'accounts/employee_form.html', {'form': form, 'employee': employee, 'action': 'Edit'})


@login_required
def employee_toggle_status(request, employee_id):
    """Enable/Disable employee (Admin only)"""
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:employee_dashboard')
    
    employee = get_object_or_404(Employee, id=employee_id)
    
    if employee.status == 'Active':
        employee.status = 'Inactive'
        messages.success(request, f'Employee {employee.emp_id} disabled.')
    else:
        employee.status = 'Active'
        messages.success(request, f'Employee {employee.emp_id} enabled.')
    
    employee.save()
    return redirect('accounts:employee_list')

