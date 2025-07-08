#!/usr/bin/env python
"""
Test script to simulate the complete appointment booking process
"""

import os
import sys
import django
import json
from django.test import Client

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('.')
django.setup()

from django.contrib.auth.models import User
from appointment.models import Service, StaffMember, AppointmentRequest

def test_complete_booking_flow():
    """Test the complete appointment booking flow"""
    
    print("=== Testing Complete Appointment Booking Flow ===\n")
    
    # Create a test client (simulates browser requests)
    client = Client(HTTP_HOST='localhost')
    
    # Step 1: Login with a test user
    print("1. Logging in...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    response = client.post('/users/signin/', login_data, follow=True)
    print(f"   Login status: {response.status_code}")
    if response.status_code == 200:
        print("   ✓ Login successful")
    else:
        print("   ✗ Login failed")
        return
    
    # Step 2: Access booking page
    print("\n2. Accessing booking page...")
    response = client.get('/booking/')
    print(f"   Booking page status: {response.status_code}")
    
    # Step 3: Access service booking page
    print("\n3. Accessing service booking page...")
    response = client.get('/booking/request/1/')
    print(f"   Service booking page status: {response.status_code}")
    if response.status_code == 200:
        print("   ✓ Service booking page accessible")
    else:
        print("   ✗ Service booking page failed")
        return
    
    # Step 4: Test AJAX endpoints
    print("\n4. Testing AJAX endpoints...")
    
    # Test staff info
    response = client.get('/booking/ajax/request_staff_info/?staff_member=1')
    print(f"   Staff info AJAX status: {response.status_code}")
    if response.status_code == 200:
        print("   ✓ Staff info AJAX working")
    
    # Test available slots
    response = client.get('/booking/ajax/available_slots/?selected_date=2025-07-08&staff_member=1')
    print(f"   Available slots AJAX status: {response.status_code}")
    if response.status_code == 200:
        slots_data = json.loads(response.content)
        print(f"   ✓ Available slots AJAX working")
        print(f"     Available slots: {len(slots_data.get('available_slots', []))}")
        if slots_data.get('available_slots'):
            print(f"     First few slots: {slots_data['available_slots'][:3]}")
    
    # Step 5: Test form submission
    print("\n5. Testing appointment form submission...")
    
    # Get CSRF token first
    response = client.get('/booking/request/1/')
    csrf_token = None
    if 'csrfmiddlewaretoken' in response.context:
        csrf_token = response.context['csrfmiddlewaretoken']
    else:
        # Extract from rendered content
        content = response.content.decode()
        import re
        csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', content)
        if csrf_match:
            csrf_token = csrf_match.group(1)
    
    if not csrf_token:
        print("   ✗ Could not get CSRF token")
        return
    
    # Submit appointment request
    form_data = {
        'csrfmiddlewaretoken': csrf_token,
        'staff_member': '1',  # David Mwesigwa
        'date': '2025-07-08',
        'start_time': '10:00:00',
        'end_time': '10:30:00',
        'service': '1'  # Medical Service
    }
    
    print(f"   Submitting form with data: {form_data}")
    response = client.post('/booking/request-submit/', form_data, follow=True)
    print(f"   Form submission status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✓ Form submission successful")
        # Check if we were redirected to client information page
        if 'client-info' in response.request['PATH_INFO'] or 'appointment' in response.request['PATH_INFO']:
            print("   ✓ Redirected to client information page")
        else:
            print(f"   Current URL: {response.request['PATH_INFO']}")
    else:
        print("   ✗ Form submission failed")
        print(f"   Response content: {response.content[:500]}")
    
    # Step 6: Check if appointment request was created
    print("\n6. Checking appointment requests...")
    requests_count = AppointmentRequest.objects.count()
    print(f"   Total appointment requests: {requests_count}")
    
    if requests_count > 0:
        latest_request = AppointmentRequest.objects.last()
        print(f"   Latest request: {latest_request.date} {latest_request.start_time} with {latest_request.staff_member.get_staff_member_name()}")
        print("   ✓ Appointment request created successfully")
    
    print(f"\n=== Booking Flow Test Complete ===")

if __name__ == '__main__':
    test_complete_booking_flow()
