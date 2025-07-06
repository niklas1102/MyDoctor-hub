# appointment/integration_views.py

"""
Integration views to bridge the new appointment system with the existing MyDoctor application.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Q
from datetime import datetime, timedelta

from .models import Service, StaffMember, Appointment, AppointmentRequest
from .forms import AppointmentRequestForm
from appointments.models import Appointment as LegacyAppointment

User = get_user_model()


@login_required
def booking_home(request):
    """
    Main booking page that shows available services and allows users to book appointments.
    """
    services = Service.objects.all()
    staff_members = StaffMember.objects.all()
    
    # Get recent appointments for the user
    recent_appointments = []
    if hasattr(request.user, 'appointment_set'):
        recent_appointments = request.user.appointment_set.all().order_by('-created_at')[:5]
    
    context = {
        'services': services,
        'staff_members': staff_members,
        'recent_appointments': recent_appointments,
        'segment': 'appointments',
    }
    
    return render(request, 'appointment/booking_home.html', context)


@login_required
def service_booking(request, service_id):
    """
    Service-specific booking page - redirects to the modern calendar-based appointment system.
    """
    # Redirect to the modern calendar-based appointment system
    return redirect('appointment:appointment_request', service_id=service_id)


@login_required
def my_appointments(request):
    """
    Display user's appointments from both systems.
    """
    # Get appointments from new system
    new_appointments = Appointment.objects.filter(client=request.user).order_by('-created_at')
    
    # Get appointments from legacy system
    legacy_appointments = LegacyAppointment.objects.filter(
        Q(patient=request.user) | Q(doctor=request.user)
    ).order_by('-created_at')
    
    context = {
        'new_appointments': new_appointments,
        'legacy_appointments': legacy_appointments,
        'segment': 'appointments',
    }
    
    return render(request, 'appointment/my_appointments.html', context)


@login_required
def booking_confirmation(request, appointment_id):
    """
    Booking confirmation page.
    """
    appointment = get_object_or_404(Appointment, id=appointment_id, client=request.user)
    
    context = {
        'appointment': appointment,
        'segment': 'appointments',
    }
    
    return render(request, 'appointment/booking_confirmation.html', context)


@login_required
def cancel_appointment(request, appointment_id):
    """
    Cancel an appointment.
    """
    appointment = get_object_or_404(Appointment, id=appointment_id, client=request.user)
    
    if request.method == 'POST':
        # Instead of deleting, we could add a status field
        appointment.delete()
        messages.success(request, 'Your appointment has been canceled successfully!')
        return redirect('appointment:my_appointments')
    
    context = {
        'appointment': appointment,
        'segment': 'appointments',
    }
    
    return render(request, 'appointment/cancel_appointment.html', context)


def get_available_slots_api(request):
    """
    API endpoint to get available slots for a staff member on a specific date.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    staff_member_id = request.GET.get('staff_member_id')
    date_str = request.GET.get('date')
    
    if not staff_member_id or not date_str:
        return JsonResponse({'error': 'Staff member ID and date are required'}, status=400)
    
    try:
        staff_member = StaffMember.objects.get(id=staff_member_id)
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (StaffMember.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Invalid staff member or date'}, status=400)
    
    # Get available slots (this would need to be implemented based on the appointment system logic)
    # For now, return a simple response
    slots = []
    
    return JsonResponse({
        'slots': slots,
        'date': date_str,
        'staff_member': staff_member.get_staff_member_name(),
    })
