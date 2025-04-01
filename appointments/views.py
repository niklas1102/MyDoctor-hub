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
from .models import Encounter  # Ensure Encounter model is imported
from django.db.models import Count
from .models import LabResult  # Import LabResult model
from .models import Prescription  # Import Prescription model
from .models import Document  # Import Document model
from django.urls import reverse
from django.http import JsonResponse
from .models import Diagnosis, Medication, Immunization  # Ensure related models are imported
import json

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

@login_required(login_url='/users/signin/')
@user_passes_test(is_doctor)
def doctor_patient_lookup(request):
    patients = User.objects.filter(groups__name='Patient').select_related('profile')  # Ensure profile includes dob
    context = {
        'patients': patients,
        'segment': 'doctor_patient_lookup',
    }
    return render(request, 'appointments/doctor_patient_lookup.html', context)

@login_required(login_url='/users/signin/')
@user_passes_test(is_doctor)
def doctor_patient_overview(request, patient_id):
    patient = get_object_or_404(User, id=patient_id, groups__name='Patient')
    encounters = Encounter.objects.filter(patient=patient).select_related('doctor').order_by('-date')

    # Generate health summary
    health_summary = {
        'conditions': ["Diabetes", "Hypertension"],  # Replace with FHIR Condition data
        'medications': ["Metformin", "Lisinopril"],  # Replace with FHIR MedicationRequest data
        'last_immunization_date': "2023-03-15",  # Replace with FHIR Immunization data
        'completed_visits': encounters.filter(status="Closed").count(),
    }

    # Generate timeline data
    timeline = [
        {
            'date': encounter.date,
            'type': 'Visit',
            'description': f"Visit completed by Dr. {encounter.doctor.get_full_name()}",
            'link': reverse('appointments:doctor_encounter_view', args=[encounter.id])
        } for encounter in encounters
    ]
    # Add other events (e.g., lab results, prescriptions, uploads) to the timeline
    timeline += [
        {
            'date': lab_result.date,
            'type': 'Lab Result',
            'description': f"Lab result for {lab_result.test_type} uploaded",
            'link': lab_result.file.url if lab_result.file else None  # Use file.url if file exists
        } for lab_result in LabResult.objects.filter(patient=patient).order_by('-date')
    ]
    timeline += [
        {
            'date': prescription.date,
            'type': 'Prescription',
            'description': f"Prescription for {prescription.medication_name} issued by Dr. {prescription.doctor.get_full_name()}",
            'link': None
        } for prescription in Prescription.objects.filter(patient=patient).order_by('-date')
    ]
    timeline += [
        {
            'date': document.upload_date,
            'type': 'Upload',
            'description': f"Document '{document.title}' uploaded",
            'link': document.file.url if document.file else None  # Check if file exists
        } for document in Document.objects.filter(patient=patient).order_by('-upload_date')
    ]

    # Sort timeline by date in reverse chronological order
    timeline = sorted(timeline, key=lambda x: x['date'], reverse=True)

    context = {
        'patient': patient,
        'encounters': encounters,
        'health_summary': health_summary,
        'timeline': timeline,
        'segment': 'doctor_patient_overview',
    }
    return render(request, 'appointments/doctor_patient_overview.html', context)

@login_required(login_url='/users/signin/')
@user_passes_test(is_doctor)
def doctor_encounter_view(request, encounter_id):
    if encounter_id == 0:
        # Handle new encounter creation
        patient_id = request.GET.get('patient_id')  # Get patient_id from query parameters
        if patient_id:
            patient = get_object_or_404(User, id=patient_id, groups__name='Patient')
            encounter = Encounter.objects.create(
                doctor=request.user,
                patient=patient,
                status='Active'
            )
            messages.success(request, 'New encounter created successfully.')
            return redirect(reverse('appointments:doctor_encounter_view', args=[encounter.id]))
        elif request.method == 'POST':
            patient_id = request.POST.get('patient_id')
            patient = get_object_or_404(User, id=patient_id, groups__name='Patient')
            encounter = Encounter.objects.create(
                doctor=request.user,
                patient=patient,
                status='Active'
            )
            messages.success(request, 'New encounter created successfully.')
            return redirect(reverse('appointments:doctor_encounter_view', args=[encounter.id]))
        else:
            # Render a form to select a patient for the new encounter
            patients = User.objects.filter(groups__name='Patient')
            context = {
                'patients': patients,
                'segment': 'doctor_encounter_view',
            }
            return render(request, 'appointments/new_encounter.html', context)

    # Handle existing encounter
    encounter = get_object_or_404(Encounter, id=encounter_id)

    # Fetch related data
    diagnoses = encounter.diagnoses.all()
    medications = encounter.medications.all()
    immunizations = encounter.immunizations.all()
    lab_results = encounter.labresults.all()
    documents = encounter.documents.all()

    # Handle saving notes separately
    if request.method == 'POST' and 'save_notes' in request.POST:
        notes = request.POST.get('notes', '').strip()
        encounter.notes = notes if notes else None  # Avoid empty strings
        encounter.save()  # Save the updated notes to the database
        messages.success(request, 'Notes saved successfully.')
        return redirect(reverse('appointments:doctor_encounter_view', args=[encounter.id]))  # Redirect to the same view

    # Handle finalizing the encounter
    if encounter.status != 'Closed' and request.method == 'POST' and 'end_visit' in request.POST:
        # Save notes
        notes = request.POST.get('notes', '').strip()
        encounter.notes = notes if notes else None
        encounter.save()

        # Parse the JSON data from hidden fields
        diagnoses_data = json.loads(request.POST.get('diagnoses_data', '[]'))
        meds_data = json.loads(request.POST.get('medications_data', '[]'))
        imms_data = json.loads(request.POST.get('immunizations_data', '[]'))
        labs_data = json.loads(request.POST.get('labresults_data', '[]'))
        docs_data = json.loads(request.POST.get('documents_data', '[]'))

        # Create Diagnosis entries
        for d in diagnoses_data:
            Diagnosis.objects.create(encounter=encounter, description=d)

        # Create Medication entries
        for m in meds_data:
            Medication.objects.create(
                encounter=encounter,
                name=m.get('name', ''),
                dosage=m.get('dosage', ''),
                duration=m.get('duration', '')
            )

        # Create Immunizations
        for i in imms_data:
            Immunization.objects.create(
                encounter=encounter,
                name=i.get('name', ''),
                date=i.get('date', ''),
                dose=i.get('dose', ''),
                status=i.get('status', '')
            )

        # Create LabResults
        for lab in labs_data:
            LabResult.objects.create(
                encounter=encounter,
                patient=encounter.patient,
                test_type=lab.get('testType', ''),
                status=lab.get('status', 'Pending')
            )

        # Create Documents
        for doc in docs_data:
            Document.objects.create(
                encounter=encounter,
                patient=encounter.patient,
                title=doc.get('title', ''),
                doc_type=doc.get('type', '')
            )

        # Mark encounter as closed
        encounter.status = 'Closed'
        encounter.save()
        messages.success(request, 'The visit has been finalized successfully.')
        return redirect(reverse('appointments:doctor_patient_overview', args=[encounter.patient.id]))

    context = {
        'encounter': encounter,
        'diagnoses': diagnoses,
        'medications': medications,
        'immunizations': immunizations,
        'lab_results': lab_results,
        'documents': documents,
        'segment': 'doctor_encounter_view',
    }
    return render(request, 'appointments/doctor_encounter_view.html', context)

@login_required(login_url='/users/signin/')
def upload_document(request):
    Document = apps.get_model('users', 'Document')  # Dynamically load the Document model

    if request.method == 'POST':
        title = request.POST.get('title')
        doc_type = request.POST.get('doc_type')
        file = request.FILES.get('file')

        if title and doc_type and file:  # Ensure a file is provided
            Document.objects.create(title=title, doc_type=doc_type, file=file, user=request.user)
            messages.success(request, 'Document uploaded successfully.')
        else:
            messages.error(request, 'All fields, including the file, are required.')

    return redirect('profile')  # Redirect back to the profile page

@login_required(login_url='/users/signin/')
@user_passes_test(is_doctor)
def search_patients(request):
    query = request.GET.get('query', '').strip()
    if query:
        patients = User.objects.filter(
            Q(groups__name='Patient') &
            (Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(id__icontains=query))  # Properly close parentheses here
        ).values('id', 'first_name', 'last_name')
        return JsonResponse(list(patients), safe=False)
    return JsonResponse([], safe=False)

def some_view(request):
    # Ensure patient IDs are handled correctly
    patient = Patient.objects.get(id="12345")  # Example usage
