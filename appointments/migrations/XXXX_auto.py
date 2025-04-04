from django.db import migrations, models


def set_default_file(apps, schema_editor):
    # Dynamically load the Document model from the correct app
    Document = apps.get_model(
        "users", "Document"
    )  # Use 'users' app instead of 'appointments'
    for document in Document.objects.filter(file__isnull=True):
        document.file = "documents/default-file.txt"
        document.save()


class Migration(migrations.Migration):

    dependencies = [
        ("appointments", "0004_alter_appointment_reason"),  # Updated dependency
    ]

    operations = [
        migrations.RunPython(set_default_file),
    ]
