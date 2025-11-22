# Quick Start Guide

## Installation Steps

1. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

2. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

3. **Create superuser (Admin account)**
```bash
python manage.py createsuperuser
```
Enter username, email, and password when prompted.

4. **Run the development server**
```bash
python manage.py runserver
```

5. **Access the application**
- Open browser: `http://127.0.0.1:8000`
- Login with the superuser credentials

## Initial Setup

1. **Configure System Settings**
   - Go to Django Admin: `http://127.0.0.1:8000/admin`
   - Navigate to "System Settings"
   - Configure:
     - Office start time (default: 09:00)
     - Late cutoff time (default: 09:15)
     - Half-day cutoff time (default: 12:00)
     - Penalty settings

2. **Add Employees**
   - Login as Admin
   - Go to "Employees" menu
   - Click "Add Employee"
   - Fill in employee details
   - Employee ID will be auto-generated (6 digits)

3. **Set Employee Joining Date**
   - Important: Set the joining date for each employee
   - This determines the salary cycle (not calendar month)

## Key Features Usage

### Attendance
- **Employees**: Clock IN/OUT from dashboard
- **Admin**: View all attendance, manually add/edit records

### Collections
- **Admin**: Add daily collections
- System automatically calculates incentives based on ₹1950 rule

### Payroll
- **Admin**: Generate salary for employees
- Salary period is calculated from joining date
- Download PDF salary slips

### Dashboards
- **Admin**: Comprehensive dashboard with charts and metrics
- **Employee**: Simplified dashboard with personal stats

## Incentive Calculation Rule

- ₹1950 collected once → ₹0 incentive (Agency)
- Every second ₹1950 → ₹500 incentive
- Example:
  - ₹1950 × 1 = ₹0
  - ₹1950 × 2 = ₹500
  - ₹1950 × 4 = ₹1000
  - ₹1950 × 6 = ₹1500

## Salary Cycle

Salary periods are based on employee joining date, not calendar month.

Example:
- Employee joined: 22/11/2025
- First salary period: 22/11/2025 to 21/12/2025
- Second salary period: 22/12/2025 to 21/01/2026

## Troubleshooting

**Issue**: Charts not displaying
- Solution: Ensure JavaScript is enabled in browser

**Issue**: PDF generation fails
- Solution: Ensure ReportLab is installed: `pip install reportlab`

**Issue**: Database errors
- Solution: Run migrations: `python manage.py migrate`

## Production Deployment

1. Set `DEBUG = False` in `settings.py`
2. Configure proper database (PostgreSQL recommended)
3. Set `SECRET_KEY` environment variable
4. Configure static files serving
5. Set up proper domain in `ALLOWED_HOSTS`

