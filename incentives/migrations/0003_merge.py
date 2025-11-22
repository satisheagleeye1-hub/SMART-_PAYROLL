# Merge migration to resolve conflicting 0002 migrations
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('incentives', '0002_alter_dailycollection_unique_together_and_more'),
        ('incentives', '0002_remove_unique_together'),
    ]

    operations = [
        # This merge migration intentionally does nothing; it resolves the divergent migration history.
    ]

