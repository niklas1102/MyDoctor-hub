from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('appointments', '0015_delete_user'),  # Reference the migration before the merge
    ]

    operations = [
        # No operations here; logic moved to a new migration
    ]
