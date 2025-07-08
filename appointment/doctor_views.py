# appointment/doctor_views.py

"""
Doctor-specific views for appointment management
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import json

from .models import Appointment, StaffMember
from appointments.models import Appointment as LegacyAppointment

User = get_user_model()


def is_doctor(user):
    """Check if user is a doctor"""
    return user.groups.filter(name='Doctor').exists()


@login_required
@user_passes_test(is_doctor)
def doctor_dashboard(request):
    """
    Doctor dashboard showing appointment overview and quick actions
    """
    # Get legacy appointments
    legacy_appointments = LegacyAppointment.objects.filter(
        doctor=request.user
    ).order_by('-created_at')[:10]
    
    # Get new system appointments
    try:
        staff_member = StaffMember.objects.get(user=request.user)
        new_appointments = Appointment.objects.filter(
            appointment_request__staff_member=staff_member
        ).order_by('-created_at')[:10]
    except StaffMember.DoesNotExist:
        new_appointments = []
    
    # Get pending appointments that need confirmation
    pending_appointments = LegacyAppointment.objects.filter(
        doctor=request.user,
        status='pending'
    ).order_by('date')
    
    # Get today's appointments
    today = timezone.now().date()
    today_appointments = LegacyAppointment.objects.filter(
        doctor=request.user,
        date__date=today,
        status='confirmed'
    ).order_by('date')
    
    context = {
        'legacy_appointments': legacy_appointments,
        'new_appointments': new_appointments,
        'pending_appointments': pending_appointments,
        'today_appointments': today_appointments,
        'segment': 'doctor_dashboard',
    }
    
    return render(request, 'appointment/doctor_dashboard.html', context)


@login_required
@user_passes_test(is_doctor)
def doctor_appointment_calendar(request):
    """
    Doctor's appointment calendar view
    """
    # Get appointments from both systems
    legacy_appointments = LegacyAppointment.objects.filter(
        doctor=request.user
    ).select_related('patient')
    
    # Get new system appointments
    try:
        staff_member = StaffMember.objects.get(user=request.user)
        new_appointments = Appointment.objects.filter(
            appointment_request__staff_member=staff_member
        ).select_related('client', 'appointment_request')
    except StaffMember.DoesNotExist:
        new_appointments = []
    
    # Format appointments for calendar
    calendar_events = []
    
    # Add legacy appointments
    for appointment in legacy_appointments:
        calendar_events.append({
            'id': f'legacy_{appointment.id}',
            'title': f'{appointment.patient.get_full_name() or appointment.patient.username} - {appointment.reason}',
            'start': appointment.date.isoformat(),
            'color': '#10b981' if appointment.status == 'confirmed' else '#f59e0b' if appointment.status == 'pending' else '#ef4444',
            'extendedProps': {
                'type': 'legacy',
                'status': appointment.status,
                'patient': appointment.patient.get_full_name() or appointment.patient.username,
                'reason': appointment.reason,
                'appointment_id': appointment.id,
            }
        })
    
    # Add new system appointments
    for appointment in new_appointments:
        start_datetime = datetime.combine(
            appointment.get_appointment_date(),
            appointment.appointment_request.start_time
        )
        end_datetime = datetime.combine(
            appointment.get_appointment_date(),
            appointment.appointment_request.end_time
        )
        
        calendar_events.append({
            'id': f'new_{appointment.id}',
            'title': f'{appointment.client.get_full_name() or appointment.client.username} - {appointment.get_service_name()}',
            'start': start_datetime.isoformat(),
            'end': end_datetime.isoformat(),
            'color': '#10b981' if appointment.is_confirmed() else '#f59e0b' if appointment.is_pending() else '#ef4444',
            'extendedProps': {
                'type': 'new',
                'status': appointment.get_status(),
                'patient': appointment.client.get_full_name() or appointment.client.username,
                'service': appointment.get_service_name(),
                'reason': appointment.appointment_request.reason or 'No reason provided',
                'appointment_id': appointment.id,
                'legacy_id': appointment.legacy_appointment_id,
            }
        })
    
    context = {
        'calendar_events': json.dumps(calendar_events),
        'segment': 'doctor_calendar',
    }
    
    return render(request, 'appointment/doctor_calendar.html', context)


@login_required
@user_passes_test(is_doctor)
def quick_confirm_appointment(request, appointment_id):
    """
    Quick appointment confirmation via AJAX
    """
    if request.method == 'POST':
        try:
            appointment = get_object_or_404(LegacyAppointment, id=appointment_id, doctor=request.user)
            
            if appointment.status == 'pending':
                appointment.status = 'confirmed'
                appointment.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Appointment confirmed successfully!',
                    'status': 'confirmed'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Appointment is not in pending status.'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error confirming appointment: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})
