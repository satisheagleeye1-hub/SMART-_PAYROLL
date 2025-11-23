deacfrom django.test import Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from attendance.models import Attendance

User = get_user_model()

username = 'quickclockuser'
password = 'QuickClock123'

user, created = User.objects.get_or_create(username=username, defaults={'email':'quickclock@test.local'})
if created:
    user.set_password(password)
    user.role = 'User'
    user.save()
else:
    user.set_password(password)
    user.save()

client = Client()
print('Logging in...')
logged_in = client.login(username=username, password=password)
print('logged_in:', logged_in)

# Ensure no existing attendance for today
today = timezone.now().date()
Attendance.objects.filter(employee=user, date=today).delete()

# Perform quick GET
resp = client.get('/attendance/clock-in/?quick=1')
print('GET quick status:', resp.status_code)

att = Attendance.objects.filter(employee=user, date=today).first()
print('attendance exists:', bool(att))
if att:
    print('in_time:', att.in_time)
    print('late_minutes:', att.late_minutes)
    print('penalty:', att.penalty)

