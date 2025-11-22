from accounts.models import Employee

if not Employee.objects.filter(username='admin').exists():
    u = Employee.objects.create_superuser(username='admin', password='adminpass', email='admin@example.com')
    u.first_name = 'System'
    u.last_name = 'Admin'
    u.role = 'Admin'
    u.save()
    print('Superuser created: admin / adminpass')
else:
    print('Superuser admin already exists')

