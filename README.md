# Smart Payroll & Incentive Management System

A comprehensive Django-based web application for managing employee attendance, payroll, and incentives with automated calculations and real-time dashboards.

## Features

### 🔐 Authentication & Authorization
- Secure login system with email/username
- Role-based access control (Admin/User)
- Password reset functionality
- Session management

### 👥 Employee Management
- Auto-generated 6-digit Employee ID
- Complete CRUD operations
- Employee status management (Active/Inactive)
- Search and filter capabilities

### ⏰ Attendance Management
- Self-service clock IN/OUT for employees
- Automatic late detection and penalty calculation
- Half-day detection
- Admin can manually add/edit attendance
- Attendance history with filters

### 💰 Daily Collections & Incentives
- Daily collection tracking
- Automatic incentive calculation based on ₹1950 rule:
  - ₹1950 × 1 = ₹0 incentive
  - ₹1950 × 2 = ₹500 incentive
  - ₹1950 × 4 = ₹1000 incentive
  - And so on...

### 💵 Payroll Management
- Salary cycle based on joining date (not calendar month)
- Automatic salary calculation including:
  - Basic salary
  - Total incentives
  - Total penalties
  - Half-day cuts
  - Net salary
- PDF salary slip generation

### 📊 Dashboards
- **Admin Dashboard:**
  - Real-time metrics (Present/Absent count, Daily collection, Incentives, Payout)
  - Monthly attendance bar chart
  - Daily collection line chart
  - Salary distribution pie chart
  - Today's attendance list
  - Recent collections
  - Low attendance alerts

- **Employee Dashboard:**
  - Today's punch status
  - Month summary (Attendance, Collection, Incentives, Penalties)
  - Latest salary slip

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd salary-machine
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser (Admin)**
```bash
python manage.py createsuperuser
```

6. **Run development server**
```bash
python manage.py runserver
```

7. **Access the application**
- Open browser: `http://127.0.0.1:8000`
- Login with superuser credentials

## Database Configuration

By default, the system uses SQLite. For production, configure PostgreSQL in `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'salary_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Project Structure

```
salary-machine/
├── accounts/          # User authentication & employee management
├── attendance/        # Attendance tracking
├── incentives/        # Daily collections & incentive calculation
├── payroll/           # Salary calculation & PDF generation
├── dashboard/         # Admin & employee dashboards
├── templates/         # HTML templates
├── static/            # Static files (CSS, JS, images)
└── salary_system/     # Main project settings
```

## API Endpoints

### Attendance API
- `POST /api/attendance/clock-in/` - Clock in
- `POST /api/attendance/clock-out/` - Clock out
- `GET /api/attendance/` - List attendance (with filters)

### Collection API
- `POST /api/collection/add/` - Add collection
- `GET /api/collection/` - List collections (with filters)

### Incentive API
- `GET /api/incentive/calc-daily/` - Calculate daily incentive

### Salary API
- `POST /api/salary/generate/` - Generate salary
- `GET /api/salary/details/<id>/` - Get salary details

## Usage

### For Admin:
1. Login with admin credentials
2. Add employees from "Employees" menu
3. View/manage attendance from "Attendance" menu
4. Add daily collections from "Collections" menu
5. Generate salaries from "Payroll" menu
6. View comprehensive dashboard with metrics and charts

### For Employees:
1. Login with employee credentials
2. Clock IN/OUT from dashboard
3. View attendance history
4. Check salary details and download PDF slips
5. View monthly summary

## System Settings

Configure attendance rules from Django Admin:
- Office start time
- Late cutoff time
- Half-day cutoff time
- Penalty per minute or fixed penalty

## Technologies Used

- **Backend:** Django 4.2, Django REST Framework
- **Frontend:** HTML5, Tailwind CSS, JavaScript, Chart.js
- **Database:** SQLite (default) / PostgreSQL
- **PDF Generation:** ReportLab

## Security Features

- CSRF protection
- Password hashing
- Role-based access control
- Input validation
- Session timeout

## License

This project is proprietary software.

## Support

For issues or questions, please contact the development team.

