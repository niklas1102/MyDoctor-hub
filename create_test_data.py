#!/usr/bin/env python
"""
Test script to create sample data for appointment system testing
"""
import os
import sys
import django

# Add the project path to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from appointment.models import Service, StaffMember
from datetime import time, timedelta

User = get_user_model()

def create_test_data():
    """Create test data for appointment system"""
    print("Creating test data for appointment system...")
    
    # Create Doctor group if it doesn't exist
    doctor_group, created = Group.objects.get_or_create(name='Doctor')
    patient_group, created = Group.objects.get_or_create(name='Patient')
    
    print("✓ Created user groups")
    
    # Create a test doctor
    doctor, created = User.objects.get_or_create(
        username='doctor1',
        email='doctor1@example.com',
        defaults={
            'first_name': 'Dr. Jane',
            'last_name': 'Smith',
            'is_staff': True,
        }
    )
    if created:
        doctor.set_password('password123')
        doctor.save()
    
    doctor.groups.add(doctor_group)
    print("✓ Created test doctor: doctor1@example.com")
    
    # Create a test patient
    patient, created = User.objects.get_or_create(
        username='patient1',
        email='patient1@example.com',
        defaults={
            'first_name': 'John',
            'last_name': 'Doe',
        }
    )
    if created:
        patient.set_password('password123')
        patient.save()
    
    patient.groups.add(patient_group)
    print("✓ Created test patient: patient1@example.com")
    
    # Create a test service
    service, created = Service.objects.get_or_create(
        name='General Consultation',
        defaults={
            'description': 'General medical consultation',
            'duration': timedelta(minutes=30),
            'price': 50.00,
            'currency': 'USD',
            'is_active': True,
        }
    )
    print("✓ Created test service: General Consultation")
    
    # Create staff member for the doctor
    staff_member, created = StaffMember.objects.get_or_create(
        user=doctor,
        defaults={
            'slot_duration': 30,
            'lead_time': time(9, 0),
            'finish_time': time(17, 0),
            'appointment_buffer_time': 30,
            'work_on_saturday': True,
            'work_on_sunday': False,
        }
    )
    
    # Add service to staff member
    staff_member.services_offered.add(service)
    print("✓ Created staff member for doctor")
    
    print("\nTest data created successfully!")
    print("\nYou can now test the appointment system with:")
    print("- Doctor: doctor1@example.com / password123")
    print("- Patient: patient1@example.com / password123")
    print("- Service: General Consultation")
    print("\nTo test the appointment flow:")
    print("1. Login as patient1@example.com")
    print("2. Go to /appointment/ to book an appointment")
    print("3. Select General Consultation service")
    print("4. Choose a date and time")
    print("5. Login as doctor1@example.com")
    print("6. Go to /appointments/doctor-appointments/ to see and confirm the appointment")

if __name__ == '__main__':
    create_test_data()
