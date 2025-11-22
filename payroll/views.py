from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, date, timedelta
from decimal import Decimal
from .models import Salary
from accounts.models import Employee
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT


@login_required
def salary_list(request):
    """View all salaries (Admin) or own salaries (Employee)"""
    if request.user.is_admin:
        salaries = Salary.objects.all().order_by('-end_date')
        
        # Filter by employee
        employee_id = request.GET.get('employee')
        if employee_id:
            salaries = salaries.filter(employee__emp_id=employee_id)
    else:
        salaries = Salary.objects.filter(employee=request.user).order_by('-end_date')
    
    employees = Employee.objects.filter(status='Active').order_by('emp_id') if request.user.is_admin else None
    
    context = {
        'salaries': salaries[:50],
        'employees': employees,
        'employee_id': request.GET.get('employee'),
    }
    return render(request, 'payroll/salary_list.html', context)


@login_required
def generate_salary(request, employee_id=None):
    """Generate salary for an employee (Admin only)"""
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:employee_dashboard')
    
    if employee_id:
        employee = get_object_or_404(Employee, emp_id=employee_id)
    else:
        employee_id = request.GET.get('employee')
        if employee_id:
            employee = get_object_or_404(Employee, emp_id=employee_id)
        else:
            # Show form to select employee
            employees = Employee.objects.filter(status='Active').order_by('emp_id')
            return render(request, 'payroll/generate_salary.html', {'employees': employees})
    
    # Get salary period
    reference_date = request.GET.get('reference_date')
    if reference_date:
        ref_date = datetime.strptime(reference_date, '%Y-%m-%d').date()
    else:
        ref_date = timezone.now().date()
    
    start_date, end_date = Salary.get_salary_period(employee, ref_date)
    
    if not start_date or not end_date:
        messages.error(request, 'Employee joining date is not set.')
        return redirect('payroll:salary_list')
    
    # Check if salary already exists for this period
    existing = Salary.objects.filter(
        employee=employee,
        start_date=start_date,
        end_date=end_date
    ).first()
    
    if existing:
        salary = existing
        salary.calculate_salary()
        salary.save()
        messages.success(request, 'Salary recalculated successfully.')
    else:
        salary = Salary(
            employee=employee,
            start_date=start_date,
            end_date=end_date,
            basic_salary=employee.basic_salary
        )
        salary.calculate_salary()
        salary.save()
        messages.success(request, 'Salary generated successfully.')
    
    return redirect('payroll:salary_detail', salary_id=salary.id)


@login_required
def salary_detail(request, salary_id):
    """View salary details"""
    salary = get_object_or_404(Salary, id=salary_id)
    
    # Check if user has access
    if not request.user.is_admin and salary.employee != request.user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:employee_dashboard')
    
    return render(request, 'payroll/salary_detail.html', {'salary': salary})


@login_required
def generate_salary_slip_pdf(request, salary_id):
    """Generate PDF salary slip"""
    salary = get_object_or_404(Salary, id=salary_id)
    
    # Check if user has access
    if not request.user.is_admin and salary.employee != request.user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:employee_dashboard')
    
    # Create PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="salary_slip_{salary.employee.emp_id}_{salary.end_date}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    elements.append(Paragraph("SALARY SLIP", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Company Info
    company_style = ParagraphStyle(
        'Company',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER
    )
    elements.append(Paragraph("Smart Payroll & Incentive Management System", company_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Employee Details
    emp_data = [
        ['Employee ID:', salary.employee.emp_id],
        ['Name:', salary.employee.get_full_name() or salary.employee.username],
        ['Email:', salary.employee.email],
        ['Phone:', salary.employee.phone or 'N/A'],
        ['Period:', f"{salary.start_date} to {salary.end_date}"],
    ]
    
    emp_table = Table(emp_data, colWidths=[2*inch, 4*inch])
    emp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    elements.append(emp_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Salary Breakdown
    salary_data = [
        ['Description', 'Amount (₹)'],
        ['Basic Salary', f"{salary.basic_salary:,.2f}"],
        ['Total Incentive', f"{salary.total_incentive:,.2f}"],
        ['Total Penalty', f"-{salary.total_penalty:,.2f}"],
        ['Half-Day Cuts', f"{salary.half_day_cuts} days"],
        ['', ''],
        ['Net Salary', f"{salary.net_salary:,.2f}"],
    ]
    
    salary_table = Table(salary_data, colWidths=[4*inch, 2*inch])
    salary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    elements.append(salary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Attendance Summary
    att_data = [
        ['Total Working Days', str(salary.total_working_days)],
        ['Total Present Days', str(salary.total_present_days)],
        ['Absent Days', str(salary.total_working_days - salary.total_present_days)],
    ]
    
    att_table = Table(att_data, colWidths=[3*inch, 3*inch])
    att_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    elements.append(att_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Signature Section
    signature_style = ParagraphStyle(
        'Signature',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER
    )
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("_________________________", signature_style))
    elements.append(Paragraph("Authorized Signature", signature_style))
    
    # Build PDF
    doc.build(elements)
    return response

