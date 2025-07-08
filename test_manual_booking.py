#!/usr/bin/env python
"""
Simple manual test to verify booking functionality
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('.')
django.setup()

from appointment.models import Service, StaffMember, AppointmentRequest

def test_booking_data():
    """Test the booking data setup"""
    
    print("=== Manual Booking Test ===\n")
    
    # Check services
    services = Service.objects.all()
    print(f"Services available: {services.count()}")
    for service in services:
        print(f"  - {service.name}: {service.duration} duration")
    
    # Check staff
    staff = StaffMember.objects.all()
    print(f"\nStaff members available: {staff.count()}")
    for member in staff:
        print(f"  - {member.get_staff_member_name()}")
        print(f"    Services: {[s.name for s in member.services_offered.all()]}")
        print(f"    Working hours: {member.workinghours_set.count()} days configured")
    
    # Check recent appointment requests
    recent_requests = AppointmentRequest.objects.order_by('-created_at')[:5]
    print(f"\nRecent appointment requests: {recent_requests.count()}")
    for req in recent_requests:
        print(f"  - {req.date} {req.start_time}-{req.end_time} with {req.staff_member.get_staff_member_name()}")
        print(f"    Service: {req.service.name}, Created: {req.created_at}")
    
    print("\n=== Test Complete ===")

if __name__ == '__main__':
    test_booking_data()
