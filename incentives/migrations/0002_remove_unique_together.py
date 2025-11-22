# Generated migration to remove unique_together on DailyCollection
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('incentives', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dailycollection',
            options={'verbose_name_plural': 'Daily Collections', 'ordering': ['-date']},
        ),
        migrations.AlterUniqueTogether(
            name='dailycollection',
            unique_together=set(),
        ),
    ]
