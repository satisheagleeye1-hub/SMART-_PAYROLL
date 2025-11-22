"""
Setup script for Smart Payroll System
Run this after installing dependencies to set up the database and create initial data
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'salary_system.settings')
django.setup()

from django.core.management import call_command
from accounts.models import SystemSettings

def setup():
    print("Setting up Smart Payroll System...")
    
    # Run migrations
    print("\n1. Running migrations...")
    call_command('migrate', verbosity=1)
    
    # Create system settings if not exists
    print("\n2. Creating system settings...")
    SystemSettings.get_settings()
    print("   ✓ System settings created")
    
    print("\n✓ Setup complete!")
    print("\nNext steps:")
    print("1. Create a superuser: python manage.py createsuperuser")
    print("2. Run the server: python manage.py runserver")
    print("3. Access the application at http://127.0.0.1:8000")

if __name__ == '__main__':
    setup()

