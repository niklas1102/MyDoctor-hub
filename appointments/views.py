# appointments/views.py

from django import forms
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import Appointment
from .forms import AppointmentForm
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test

User = get_user_model()

def is_doctor(user):
    return user.groups.filter(name='Doctor').exists()

def is_patient(user):
    return user.groups.filter(name='Patient').exists()

def is_doctor_or_patient(user):
    return user.groups.filter(name='Doctor').exists() or user.groups.filter(name='Patient').exists()

@login_required(login_url='/users/signin/')
@user_passes_test(is_doctor_or_patient)
def appointment_list(request):
    if request.user.groups.filter(name='Doctor').exists():
        return redirect('appointments:doctor_appointments')
    appointments = Appointment.objects.filter(patient=request.user).select_related('doctor', 'patient')
    context = {
        'appointments': appointments,
        'user': request.user,
        'is_doctor': request.user.groups.filter(name='Doctor').exists(),
        'is_patient': request.user.groups.filter(name='Patient').exists(),
    }
    return render(request, 'appointments/appointment_list.html', context)

@login_required(login_url='/users/signin/')
@user_passes_test(is_patient)
def book_appointment(request):
    existing_appointments = Appointment.objects.filter(
        Q(status='pending') | Q(status__isnull=True), patient=request.user
    )
    if existing_appointments.exists():
        messages.warning(request, 'You already have an appointment booked. Please cancel it before booking a new one.')
        return redirect('appointments:appointment_list')
    if request.method == 'POST':
        form = AppointmentForm(request.POST) 
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            if not appointment.doctor.first_name or not appointment.doctor.last_name:
                messages.error(request, 'Selected doctor does not have a valid name.')
                return redirect('appointments:book_appointment')
            appointment.save()
            # Send email notifications
            subject = 'New Appointment Booking'
            message = f"You have a new appointment with {appointment.doctor.get_full_name()} on {appointment.date.strftime('%Y-%m-%d %H:%M')}."
            send_mail(
                subject,
                message,
                'your-email@example.com',
                [appointment.doctor.email, request.user.email],
                fail_silently=False,
            )
            messages.success(request, 'Your appointment has been booked!')
            return redirect('appointments:appointment_list')
    else:
        form = AppointmentForm()
    context = {
        'form': form,
        'segment': 'book_appointment',
        'is_doctor': request.user.groups.filter(name='Doctor').exists(),
        'is_patient': request.user.groups.filter(name='Patient').exists(),
    }
    return render(request, 'appointments/book_appointment.html', context)

@login_required(login_url='/users/signin/')
@user_passes_test(is_patient)
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if appointment.patient == request.user or appointment.doctor == request.user:
        appointment.delete()
        messages.success(request, 'Appointment has been canceled.')
    else:
        messages.error(request, 'You do not have permission to cancel this appointment.')
    return redirect('appointments:appointment_list')

@login_required(login_url='/users/signin/')
@user_passes_test(is_doctor)
def doctor_appointments(request):
    appointments = Appointment.objects.filter(doctor=request.user).select_related('patient')
    context = {
        'appointments': appointments,
        'user': request.user,
        'is_doctor': request.user.groups.filter(name='Doctor').exists(),
        'is_patient': request.user.groups.filter(name='Patient').exists(),
    }
    return render(request, 'appointments/doctor_appointments.html', context)

@login_required(login_url='/users/signin/')
@user_passes_test(is_doctor)
def doctor_calendar(request):
    appointments = Appointment.objects.filter(doctor=request.user).select_related('patient')
    context = {
        'appointments': appointments,
        'user': request.user,
        'is_doctor': request.user.groups.filter(name='Doctor').exists(),
        'is_patient': request.user.groups.filter(name='Patient').exists(),
    }
    return render(request, 'appointments/doctor_calendar.html', context)
