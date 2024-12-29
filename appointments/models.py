# appointments/models.py

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
    ]
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='appointments_as_doctor',
        on_delete=models.CASCADE
    )
    patient = models.ForeignKey(
        User,
        related_name='patient_appointments',
        on_delete=models.CASCADE
    )
    date = models.DateTimeField()
    reason = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # Add this line
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment with Dr. {self.doctor.last_name} on {self.date.strftime('%Y-%m-%d %H:%M')}"