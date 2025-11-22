from decimal import Decimal
from datetime import date

from accounts.models import Employee
from incentives.models import DailyCollection

# Find or create a test employee
username = 'test_incentive_user'
emp = Employee.objects.filter(username=username).first()
if not emp:
    emp = Employee.objects.create_user(username=username, password='testpass')
    emp.first_name = 'Test'
    emp.last_name = 'Incentive'
    emp.status = 'Active'
    emp.save()

print('Using employee:', emp)

# Use today's date
d = date.today()

# Create 3 collections of 1950
amount = Decimal('1950.00')
print('\nCreating 3 collections of 1950 on', d)
for i in range(3):
    coll = DailyCollection.objects.create(employee=emp, date=d, amount_collected=amount)
    print(f'Created id={coll.id} amount={coll.amount_collected} incentive={coll.incentive_earned}')

# Fetch all records and display incentives
print('\nFinal collection rows:')
cols = DailyCollection.objects.filter(employee=emp, date=d).order_by('created_at','pk')
for c in cols:
    print(f'id={c.id} created_at={c.created_at} amount={c.amount_collected} incentive={c.incentive_earned}')

# Show aggregate
from django.db.models import Sum
agg = cols.aggregate(total=Sum('amount_collected'), incentives=Sum('incentive_earned'))
print('\nAggregate:', agg)

