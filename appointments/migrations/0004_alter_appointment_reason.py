# Generated by Django 4.2.9 on 2025-03-28 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("appointments", "0003_alter_appointment_doctor_alter_appointment_reason"),
    ]

    operations = [
        migrations.AlterField(
            model_name="appointment",
            name="reason",
            field=models.CharField(default="No reason provided", max_length=255),
        ),
    ]
