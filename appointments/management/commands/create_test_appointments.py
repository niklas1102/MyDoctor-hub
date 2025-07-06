from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from appointments.models import Appointment
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = "Create test appointments for testing Jitsi Meet integration"

    def handle(self, *args, **kwargs):
        # Create test users if they don't exist
        doctor, created = User.objects.get_or_create(
            username='testdoctor',
            defaults={
                'email': 'doctor@test.com',
                'first_name': 'Dr. John',
                'last_name': 'Smith',
                'is_staff': True
            }
        )
        if created:
            doctor.set_password('testpass123')
            doctor.save()
            self.stdout.write(self.style.SUCCESS(f'Created doctor: {doctor.username}'))

        patient, created = User.objects.get_or_create(
            username='testpatient',
            defaults={
                'email': 'patient@test.com',
                'first_name': 'Jane',
                'last_name': 'Doe'
            }
        )
        if created:
            patient.set_password('testpass123')
            patient.save()
            self.stdout.write(self.style.SUCCESS(f'Created patient: {patient.username}'))

        # Create test appointments
        now = timezone.now()
        
        # Create a pending appointment
        pending_appointment, created = Appointment.objects.get_or_create(
            doctor=doctor,
            patient=patient,
            date=now + timedelta(days=1),
            defaults={
                'reason': 'Test consultation - Pending',
                'status': 'pending'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created pending appointment: {pending_appointment.id}'))

        # Create a confirmed appointment
        confirmed_appointment, created = Appointment.objects.get_or_create(
            doctor=doctor,
            patient=patient,
            date=now + timedelta(hours=1),
            defaults={
                'reason': 'Test consultation - Confirmed',
                'status': 'confirmed'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created confirmed appointment: {confirmed_appointment.id}'))

        self.stdout.write(self.style.SUCCESS('Test appointments created successfully!'))
        self.stdout.write(self.style.SUCCESS('Doctor login: testdoctor / testpass123'))
        self.stdout.write(self.style.SUCCESS('Patient login: testpatient / testpass123'))
