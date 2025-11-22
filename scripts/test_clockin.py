from django.test import Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from attendance.models import Attendance

User = get_user_model()

username = 'clockintestuser'
password = 'TestClockIn123'

user, created = User.objects.get_or_create(username=username, defaults={'email':'clockin@test.local'})
if created:
    user.set_password(password)
    user.role = 'User'
    user.save()
else:
    user.set_password(password)
    user.save()

client = Client()
logged_in = client.login(username=username, password=password)
print('logged_in:', logged_in)

get_resp = client.get('/attendance/clock-in/')
print('GET /attendance/clock-in/ status:', get_resp.status_code)

post_resp = client.post('/attendance/clock-in/')
print('POST /attendance/clock-in/ status:', post_resp.status_code)

# Check attendance record
today = timezone.now().date()
att = Attendance.objects.filter(employee=user, date=today).first()
print('attendance exists:', bool(att))
if att:
    print('in_time:', getattr(att, 'in_time'))
    print('out_time:', getattr(att, 'out_time'))
    print('late_minutes:', att.late_minutes)
    print('penalty:', att.penalty)

