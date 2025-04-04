# Generated by Django 4.2.9 on 2024-12-29 23:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("appointments", "0002_appointment_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="appointment",
            name="doctor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="appointments_as_doctor",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="appointment",
            name="reason",
            field=models.CharField(max_length=255),
        ),
    ]
