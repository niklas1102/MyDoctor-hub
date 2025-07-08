#!/usr/bin/env python
"""
Test script to create/update test users for appointment booking testing
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('.')
django.setup()

from django.contrib.auth.models import User

def setup_test_users():
    """Create or update test users for testing"""
    
    # Create/update admin user
    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True,
            'first_name': 'Admin',
            'last_name': 'User'
        }
    )
    admin.set_password('admin123')
    admin.save()
    print(f"Admin user {'created' if created else 'updated'}: {admin.username}")
    
    # Create/update test patient
    patient, created = User.objects.get_or_create(
        username='patient',
        defaults={
            'email': 'patient@example.com',
            'is_staff': False,
            'is_superuser': False,
            'first_name': 'Test',
            'last_name': 'Patient'
        }
    )
    patient.set_password('patient123')
    patient.save()
    print(f"Patient user {'created' if created else 'updated'}: {patient.username}")
    
    # Create/update test doctor
    doctor, created = User.objects.get_or_create(
        username='doctor',
        defaults={
            'email': 'doctor@example.com',
            'is_staff': True,
            'is_superuser': False,
            'first_name': 'Test',
            'last_name': 'Doctor'
        }
    )
    doctor.set_password('doctor123')
    doctor.save()
    print(f"Doctor user {'created' if created else 'updated'}: {doctor.username}")
    
    print("\nTest users created/updated:")
    print("Admin: admin / admin123")
    print("Patient: patient / patient123")
    print("Doctor: doctor / doctor123")

if __name__ == '__main__':
    setup_test_users()
