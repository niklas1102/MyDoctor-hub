from django.db import migrations, models
import random


def generate_random_id(Patient):
    while True:
        random_id = f"{random.randint(10000, 99999)}"
        if not Patient.objects.filter(temp_id=random_id).exists():
            return random_id


def update_patient_ids(apps, schema_editor):
    Patient = apps.get_model("appointments", "Patient")
    for patient in Patient.objects.all():
        if not patient.temp_id:  # Only update if temp_id is not already set
            patient.temp_id = generate_random_id(Patient)
            patient.save()


class Migration(migrations.Migration):
    dependencies = [
        ("appointments", "0017_patient"),
    ]

    operations = [
        # Add a temporary field for the new IDs
        migrations.AddField(
            model_name="patient",
            name="temp_id",
            field=models.CharField(max_length=5, null=True, unique=True),
        ),
        # Populate the temporary field with new IDs
        migrations.RunPython(update_patient_ids),
        # Swap the temp_id with the original id
        migrations.AlterField(
            model_name="patient",
            name="id",
            field=models.CharField(
                max_length=5, primary_key=True, unique=True, editable=False
            ),
        ),
        migrations.RemoveField(
            model_name="patient",
            name="temp_id",
        ),
    ]
