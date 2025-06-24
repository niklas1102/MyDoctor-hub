# appointments/views.py

from django import apps, forms
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from appointments.cloud_utils import create_condition
from apps.users.models import Profile
from .models import Appointment, MedicalRecords
from .forms import AppointmentForm
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from .models import Encounter  # Ensure Encounter model is imported
from django.db.models import Count
from .models import LabResult 
from .models import Prescription  
from .models import Document, Patient 
from django.urls import reverse
from django.http import JsonResponse
from .models import (
    Diagnosis,
    Medication,
    Immunization,
)
from .tasks import delete_document_from_cloud, delete_encounter_from_cloud, delete_immunization_from_cloud, delete_lab_result_from_cloud, delete_prescription_from_cloud, push_document_to_cloud, push_encounter_to_cloud, push_immunization_to_cloud, push_lab_result_to_cloud, push_patient_to_cloud, push_prescription_to_cloud, update_document_in_cloud, update_encounter_in_cloud, update_immunization_in_cloud, update_lab_result_in_cloud, update_patient_in_cloud, delete_patient_from_cloud, update_prescription_in_cloud 
import json

User = get_user_model()


def is_doctor(user):
    return user.groups.filter(name="Doctor").exists()


def is_patient(user):
    return user.groups.filter(name="Patient").exists()


def is_doctor_or_patient(user):
    return (
        user.groups.filter(name="Doctor").exists()
        or user.groups.filter(name="Patient").exists()
    )


@login_required(login_url="/users/signin/")
@user_passes_test(is_doctor_or_patient)
def appointment_list(request):
    if request.user.groups.filter(name="Doctor").exists():
        return redirect("appointments:doctor_appointments")
    appointments = Appointment.objects.filter(patient=request.user).select_related(
        "doctor", "patient"
    )
    context = {
        "appointments": appointments,
        "user": request.user,
        "is_doctor": request.user.groups.filter(name="Doctor").exists(),
        "is_patient": request.user.groups.filter(name="Patient").exists(),
    }
    return render(request, "appointments/appointment_list.html", context)


@login_required(login_url="/users/signin/")
@user_passes_test(is_patient)
def book_appointment(request):
    existing_appointments = Appointment.objects.filter(
        Q(status="pending") | Q(status__isnull=True), patient=request.user
    )
    if existing_appointments.exists():
        messages.warning(
            request,
            "You already have an appointment booked. Please cancel it before booking a new one.",
        )
        return redirect("appointments:appointment_list")
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            if not appointment.doctor.first_name or not appointment.doctor.last_name:
                messages.error(request, "Selected doctor does not have a valid name.")
                return redirect("appointments:book_appointment")
            appointment.save()
            # Send email notifications
            subject = "New Appointment Booking"
            message = f"You have a new appointment with {appointment.doctor.get_full_name()} on {appointment.date.strftime('%Y-%m-%d %H:%M')}."
            send_mail(
                subject,
                message,
                "your-email@example.com",
                [appointment.doctor.email, request.user.email],
                fail_silently=False,
            )
            messages.success(request, "Your appointment has been booked!")
            return redirect("appointments:appointment_list")
    else:
        form = AppointmentForm()
    context = {
        "form": form,
        "segment": "book_appointment",
        "is_doctor": request.user.groups.filter(name="Doctor").exists(),
        "is_patient": request.user.groups.filter(name="Patient").exists(),
    }
    return render(request, "appointments/book_appointment.html", context)


@login_required(login_url="/users/signin/")
@user_passes_test(is_patient)
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if appointment.patient == request.user or appointment.doctor == request.user:
        appointment.delete()
        messages.success(request, "Appointment has been canceled.")
    else:
        messages.error(
            request, "You do not have permission to cancel this appointment."
        )
    return redirect("appointments:appointment_list")


@login_required(login_url="/users/signin/")
@user_passes_test(is_doctor)
def doctor_appointments(request):
    appointments = Appointment.objects.filter(doctor=request.user).select_related(
        "patient"
    )
    context = {
        "appointments": appointments,
        "user": request.user,
        "is_doctor": request.user.groups.filter(name="Doctor").exists(),
        "is_patient": request.user.groups.filter(name="Patient").exists(),
        "segment": "doctor_appointments",
    }
    return render(request, "appointments/doctor_appointments.html", context)


@login_required(login_url="/users/signin/")
@user_passes_test(is_doctor)
def doctor_calendar(request):
    appointments = Appointment.objects.filter(doctor=request.user).select_related(
        "patient"
    )
    context = {
        "appointments": appointments,
        "user": request.user,
        "is_doctor": request.user.groups.filter(name="Doctor").exists(),
        "is_patient": request.user.groups.filter(name="Patient").exists(),
        "segment": "doctor_calendar",
    }
    return render(request, "appointments/doctor_calendar.html", context)


@login_required(login_url="/users/signin/")
@user_passes_test(is_doctor)
def doctor_patient_lookup(request):
    patients = User.objects.filter(groups__name="Patient").select_related(
        "profile"
    )  # Ensure profile includes dob
    context = {
        "patients": patients,
        "segment": "doctor_patient_lookup",
    }
    return render(request, "appointments/doctor_patient_lookup.html", context)


@login_required(login_url="/users/signin/")
@user_passes_test(is_doctor)
def doctor_patient_overview(request, patient_id):
    patient = get_object_or_404(User, id=patient_id, groups__name="Patient")
    encounters = (
        Encounter.objects.filter(patient=patient)
        .select_related("doctor")
        .order_by("-date")
    )

    # Generate health summary
    health_summary = {
        "conditions": ["Diabetes", "Hypertension"],  # Replace with FHIR Condition data
        "medications": [
            "Metformin",
            "Lisinopril",
        ],  # Replace with FHIR MedicationRequest data
        "last_immunization_date": "2023-03-15",  # Replace with FHIR Immunization data
        "completed_visits": encounters.filter(status="Closed").count(),
    }

    # Generate timeline data
    timeline = [
        {
            "date": encounter.date,
            "type": "Visit",
            "description": f"Visit completed by Dr. {encounter.doctor.get_full_name()}",
            "link": reverse("appointments:doctor_encounter_view", args=[encounter.id]),
        }
        for encounter in encounters
    ]
    # Add other events (e.g., lab results, prescriptions, uploads) to the timeline
    timeline += [
        {
            "date": lab_result.date,
            "type": "Lab Result",
            "description": f"Lab result for {lab_result.test_type} uploaded",
            "link": (
                lab_result.file.url if lab_result.file else None
            ),  # Use file.url if file exists
        }
        for lab_result in LabResult.objects.filter(patient=patient).order_by("-date")
    ]
    timeline += [
        {
            "date": prescription.date,
            "type": "Prescription",
            "description": f"Prescription for {prescription.medication_name} issued by Dr. {prescription.doctor.get_full_name()}",
            "link": None,
        }
        for prescription in Prescription.objects.filter(patient=patient).order_by(
            "-date"
        )
    ]
    timeline += [
        {
            "date": document.upload_date,
            "type": "Upload",
            "description": f"Document '{document.title}' uploaded",
            "link": (
                document.file.url if document.file else None
            ),  # Check if file exists
        }
        for document in Document.objects.filter(patient=patient).order_by(
            "-upload_date"
        )
    ]

    # Sort timeline by date in reverse chronological order
    timeline = sorted(timeline, key=lambda x: x["date"], reverse=True)

    context = {
        "patient": patient,
        "encounters": encounters,
        "health_summary": health_summary,
        "timeline": timeline,
        "segment": "doctor_patient_overview",
    }
    return render(request, "appointments/doctor_patient_overview.html", context)


@login_required(login_url="/users/signin/")
@user_passes_test(is_doctor)
def doctor_encounter_view(request, encounter_id):
    if encounter_id == 0:
        # Handle new encounter creation
        patient_id = request.GET.get(
            "patient_id"
        )  # Get patient_id from query parameters
        if patient_id:
            patient = get_object_or_404(User, id=patient_id, groups__name="Patient")
            encounter = Encounter.objects.create(
                doctor=request.user, patient=patient, status="Active"
            )
            
            resource_data = {
                "resourceType": "Encounter",
                "status": "active",
                "period": {"start": str(encounter.date)},
                "subject": {"reference": f"Patient/{patient.profile.uuid}"},
                "participant": [{"individual": {"reference": f"Practitioner/{request.user.profile.uuid}"}}],
            }
            push_encounter_to_cloud.delay(resource_data)
            
            messages.success(request, "New encounter created successfully.")
            return redirect(
                reverse("appointments:doctor_encounter_view", args=[encounter.id])
            )
        elif request.method == "POST":
            patient_uuid = request.POST.get("patient_uuid")
            patient = get_object_or_404(User, id=patient_uuid, groups__name="Patient")
            encounter = Encounter.objects.create(
                doctor=request.user, patient=patient, status="Active"
            )
            
            resource_data = {
                "resourceType": "Encounter",
                "status": "active",
                "period": {"start": str(encounter.date)},
                "subject": {"reference": f"Patient/{patient.profile.uuid}"},
                "participant": [{"individual": {"reference": f"Practitioner/{request.user.id}"}}],
            }
            push_encounter_to_cloud.delay(resource_data)


            messages.success(request, "New encounter created successfully.")
            return redirect(
                reverse("appointments:doctor_encounter_view", args=[encounter.id])
            )
        else:
            # Render a form to select a patient for the new encounter
            patients = User.objects.filter(groups__name="Patient")
            context = {
                "patients": patients,
                "segment": "doctor_encounter_view",
            }
            return render(request, "appointments/new_encounter.html", context)

    # Handle existing encounter
    encounter = get_object_or_404(Encounter, id=encounter_id)

    # Fetch related data
    diagnoses = encounter.diagnoses.all()
    medications = encounter.prescriptions.all()
    immunizations = encounter.immunizations.all()
    lab_results = encounter.labresults.all()
    documents = encounter.documents.all()

    # Handle saving notes separately
    if request.method == "POST" and "save_notes" in request.POST:
        notes = request.POST.get("notes", "").strip()
        encounter.notes = notes if notes else None  # Avoid empty strings
        encounter.save()  # Save the updated notes to the database
        
        updated_data = {
            "resourceType": "Encounter",
            "status": encounter.status,
            "period": {"start": str(encounter.date)},  # Corrected syntax
            "subject": {"reference": f"Patient/{encounter.patient.profile.uuid}"},
            "participant": [{"individual": {"reference": f"Practitioner/{request.user.id}"}}],
            "notes": encounter.notes,
        }
        update_encounter_in_cloud.delay(encounter.id, updated_data)  # Corrected function call
        
        messages.success(request, "Notes saved successfully.")
        return redirect(
            reverse("appointments:doctor_encounter_view", args=[encounter.id])
        )  # Redirect to the same view

    # Handle finalizing the encounter
    if (
        encounter.status != "Closed"
        and request.method == "POST"
        and "end_visit" in request.POST
    ):
        # Save notes
        notes = request.POST.get("notes", "").strip()
        encounter.notes = notes if notes else None
        encounter.save()

        # Parse the JSON data from hidden fields
        diagnoses_data = json.loads(request.POST.get("diagnoses_data", "[]"))
        meds_data = json.loads(request.POST.get("medications_data", "[]"))
        imms_data = json.loads(request.POST.get("immunizations_data", "[]"))
        labs_data = json.loads(request.POST.get("labresults_data", "[]"))
        docs_data = json.loads(request.POST.get("documents_data", "[]"))
        prescriptions_data = json.loads(request.POST.get("prescriptions_data", "[]"))

        for p in prescriptions_data:
            prescription = Prescription.objects.create(
                encounter=encounter,
                patient=encounter.patient,
                doctor=request.user,
                medication_name=p.get("name", ""),
                dosage=p.get("dosage", ""),
                duration=p.get("duration", ""),
            )
            # Push prescription to Google Cloud
            resource_data = {
                "resourceType": "MedicationRequest",
                "status": "active",
                "medicationCodeableConcept": {"text": prescription.medication_name},
                "subject": {"reference": f"Patient/{Profile.objects.get(user=prescription.patient).uuid}"},
                "encounter": {"reference": f"Encounter/{prescription.encounter.id}"},
                "dosageInstruction": [{"text": f"{prescription.dosage}, {prescription.duration}"}],
                "requester": {"reference": f"Practitioner/{prescription.doctor.profile.uuid}"},
            }
            push_prescription_to_cloud.delay(resource_data)
            
        
        # Create Diagnosis entries
        for d in diagnoses_data:
            diagnosis = Diagnosis.objects.create(encounter=encounter, description=d)
            # Push diagnosis to Google Cloud
            resource_data = {
                "resourceType": "Condition",
                "code": {"text": diagnosis.description},
                "subject": {"reference": f"Patient/{encounter.patient.profile.uuid}"},
                "encounter": {"reference": f"Encounter/{encounter.id}"},
            }
            create_condition.delay(resource_data)

        # Create Medication entries
        for m in meds_data:
            medication = Medication.objects.create(
                encounter=encounter,
                name=m.get("name", ""),
                dosage=m.get("dosage", ""),
                duration=m.get("duration", ""),
            )
            # Push medication to Google Cloud
            resource_data = {
                "resourceType": "MedicationRequest",
                "status": "active",
                "medicationCodeableConcept": {"text": medication.name},
                "subject": {"reference": f"Patient/{encounter.patient.profile.uuid}"},
                "encounter": {"reference": f"Encounter/{encounter.id}"},
                "dosageInstruction": [{"text": f"{medication.dosage}, {medication.duration}"}],
            }
            push_prescription_to_cloud.delay(resource_data)

        for i in imms_data:
            immunization = Immunization.objects.create(
                encounter=encounter,
                name=i.get("name", ""),
                date=i.get("date", ""),
                dose=i.get("dose", ""),
                status=i.get("status", ""),
            )
            # Push immunization to Google Cloud
            resource_data = {
                "resourceType": "Immunization",
                "status": immunization.status.lower(),
                "vaccineCode": {"text": immunization.name},
                "occurrenceDateTime": str(immunization.date),
                "doseQuantity": {"text": immunization.dose},
                "encounter": {"reference": f"Encounter/{encounter.id}"},
                "patient": {"reference": f"Patient/{encounter.patient.profile.uuid}"},
            }
            push_immunization_to_cloud.delay(resource_data)

        # Create LabResults
        for lab in labs_data:
            lab_result = LabResult.objects.create(
                encounter=encounter,
                patient=encounter.patient,
                file=lab.get("file", None),
                test_type=lab.get("testType", ""),
                status=lab.get("status", "Pending"),
            )
            # Push lab result to Google Cloud
            resource_data = {
                "resourceType": "DiagnosticReport",
                "status": lab_result.status,
                "subject": {"reference": f"Patient/{lab_result.patient.profile.uuid}"},
                "encounter": {"reference": f"Encounter/{lab_result.encounter.id}"},
                "code": {"text": lab_result.test_type},
                "presentedForm": [{"url": lab_result.file.url if lab_result.file else ""}],
            }
            push_lab_result_to_cloud.delay(resource_data)

        # Create Documents
        for doc in docs_data:
            document = Document.objects.create(
                encounter=encounter,
                patient=encounter.patient,
                title=doc.get("title", ""),
                doc_type=doc.get("type", ""),
            )
            # Push document to Google Cloud
            resource_data = {
                "resourceType": "DocumentReference",
                "status": "current",
                "type": {"text": document.doc_type},
                "subject": {"reference": f"Patient/{document.patient.profile.uuid}"},
                "context": {"encounter": {"reference": f"Encounter/{document.encounter.id}"}},
                "content": [{"attachment": {"url": document.file.url if document.file else "", "title": document.title}}],
            }
            push_document_to_cloud.delay(resource_data)

    context = {
        "encounter": encounter,
        "diagnoses": diagnoses,
        "medications": medications,
        "immunizations": immunizations,
        "lab_results": lab_results,
        "documents": documents,
        "segment": "doctor_encounter_view",
    }
    return render(request, "appointments/doctor_encounter_view.html", context)


@login_required(login_url="/users/signin/")
@user_passes_test(is_doctor)
def end_visit(request, encounter_id):
    encounter = get_object_or_404(Encounter, id=encounter_id)
    if encounter.status == "Closed":
        messages.error(request, "This encounter is already closed.")
        return redirect(reverse("appointments:doctor_encounter_view", args=[encounter.id]))

    if request.method == "POST":
        # Finalize the encounter
        encounter.status = "Closed"
        encounter.save()
        messages.success(request, "Encounter has been successfully closed.")
        return redirect(reverse("appointments:doctor_encounter_view", args=[encounter.id]))

    context = {
        "encounter": encounter,
        "segment": "end_visit",
    }
    return render(request, "appointments/end_visit_confirmation.html", context)


@login_required(login_url="/users/signin/")
def upload_document(request):
    Document = apps.get_model(
        "users", "Document"
    )  # Dynamically load the Document model

    if request.method == "POST":
        title = request.POST.get("title")
        doc_type = request.POST.get("doc_type")
        file = request.FILES.get("file")

        if title and doc_type and file:  # Ensure a file is provided
            Document.objects.create(
                title=title, doc_type=doc_type, file=file, user=request.user
            )
            messages.success(request, "Document uploaded successfully.")
        else:
            messages.error(request, "All fields, including the file, are required.")

    return redirect("profile")  # Redirect back to the profile page


@login_required(login_url="/users/signin/")
@user_passes_test(is_doctor)
def search_patients(request):
    query = request.GET.get("query", "").strip()
    if query:
        patients = User.objects.filter(
            Q(groups__name="Patient")
            & (
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(uuid__icontains=query)  # Use uuid instead of id
            )
        ).values("uuid", "first_name", "last_name")  # Return uuid instead of id
        return JsonResponse(list(patients), safe=False)
    return JsonResponse([], safe=False)


def some_view(request):
    # Ensure patient IDs are handled correctly
    patient = Patient.objects.get(id="12345")  # ExampleAdd Diagnosis usage