#!/usr/bin/env python
"""
Test script to verify appointment booking functionality
"""

import os
import sys
import django
import requests
from datetime import date, datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('.')
django.setup()

from appointment.models import Service, StaffMember, WorkingHours
from appointment.services import get_available_slots_for_staff

def test_appointment_booking():
    """Test the appointment booking functionality"""
    
    print("=== Testing Appointment Booking Functionality ===\n")
    
    # 1. Check if services exist
    services = Service.objects.all()
    print(f"1. Services available: {services.count()}")
    for service in services[:3]:
        print(f"   - {service.name} (ID: {service.id})")
    
    if not services.exists():
        print("   ERROR: No services found!")
        return
    
    # 2. Check if staff members exist
    staff_members = StaffMember.objects.all()
    print(f"\n2. Staff members available: {staff_members.count()}")
    for staff in staff_members[:3]:
        print(f"   - {staff.get_staff_member_name()} (ID: {staff.id})")
    
    if not staff_members.exists():
        print("   ERROR: No staff members found!")
        return
    
    # 3. Check working hours
    working_hours = WorkingHours.objects.all()
    print(f"\n3. Working hours configured: {working_hours.count()}")
    for wh in working_hours[:3]:
        print(f"   - Staff {wh.staff_member.get_staff_member_name()}: {wh.day_of_week} {wh.start_time}-{wh.end_time}")
    
    # 4. Test available slots for first staff member
    if staff_members.exists():
        staff = staff_members.first()
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        print(f"\n4. Testing available slots for {staff.get_staff_member_name()}:")
        try:
            slots_today = get_available_slots_for_staff(today, staff)
            slots_tomorrow = get_available_slots_for_staff(tomorrow, staff)
            
            print(f"   - Today ({today}): {len(slots_today)} slots")
            if slots_today:
                print(f"     First few slots: {[slot.strftime('%I:%M %p') for slot in slots_today[:3]]}")
            
            print(f"   - Tomorrow ({tomorrow}): {len(slots_tomorrow)} slots")
            if slots_tomorrow:
                print(f"     First few slots: {[slot.strftime('%I:%M %p') for slot in slots_tomorrow[:3]]}")
                
        except Exception as e:
            print(f"   ERROR getting slots: {e}")
    
    # 5. Test web endpoints
    print(f"\n5. Testing web endpoints:")
    base_url = "http://127.0.0.1:8000"
    
    endpoints_to_test = [
        "/booking/",
        "/booking/request/1/",
        "/static/css/appointments.css",
        "/static/js/appointments.js",
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "✓" if response.status_code in [200, 302] else "✗"
            print(f"   {status} {endpoint}: {response.status_code}")
            if response.status_code not in [200, 302]:
                print(f"     Content: {response.text[:100]}...")
        except Exception as e:
            print(f"   ✗ {endpoint}: ERROR - {e}")
    
    print(f"\n=== Test Complete ===")

if __name__ == '__main__':
    test_appointment_booking()
