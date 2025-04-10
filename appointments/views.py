# appointments/views.py

from django import apps, forms
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from .models import Appointment, MedicalRecords
from .forms import AppointmentForm, DocumentForm, EncounterForm, ImmunizationForm, LabResultForm, MedicalRecordsForm, PatientForm, PrescriptionForm
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
            messages.success(request, "New encounter created successfully.")
            return redirect(
                reverse("appointments:doctor_encounter_view", args=[encounter.id])
            )
        elif request.method == "POST":
            patient_id = request.POST.get("patient_id")
            patient = get_object_or_404(User, id=patient_id, groups__name="Patient")
            encounter = Encounter.objects.create(
                doctor=request.user, patient=patient, status="Active"
            )
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
    medications = encounter.medications.all()
    immunizations = encounter.immunizations.all()
    lab_results = encounter.labresults.all()
    documents = encounter.documents.all()

    # Handle saving notes separately
    if request.method == "POST" and "save_notes" in request.POST:
        notes = request.POST.get("notes", "").strip()
        encounter.notes = notes if notes else None  # Avoid empty strings
        encounter.save()  # Save the updated notes to the database
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
            Prescription.objects.create(
                encounter=encounter,
                patient=encounter.patient,
                doctor=request.user,
                medication_name=p.get("name", ""),
                dosage=p.get("dosage", ""),
                duration=p.get("duration", ""),
            )
        
        # Create Diagnosis entries
        for d in diagnoses_data:
            Diagnosis.objects.create(encounter=encounter, description=d)

        # Create Medication entries
        for m in meds_data:
            Medication.objects.create(
                encounter=encounter,
                name=m.get("name", ""),
                dosage=m.get("dosage", ""),
                duration=m.get("duration", ""),
            )

        # Create Immunizations
        for i in imms_data:
            Immunization.objects.create(
                encounter=encounter,
                name=i.get("name", ""),
                date=i.get("date", ""),
                dose=i.get("dose", ""),
                status=i.get("status", ""),
            )

        # Create LabResults
        for lab in labs_data:
            LabResult.objects.create(
                encounter=encounter,
                patient=encounter.patient,
                file = lab.get("file", None),
                test_type=lab.get("testType", ""),
                status=lab.get("status", "Pending"),
            )

        # Create Documents
        for doc in docs_data:
            Document.objects.create(
                encounter=encounter,
                patient=encounter.patient,
                title=doc.get("title", ""),
                doc_type=doc.get("type", ""),
            )

        # Mark encounter as closed
        encounter.status = "Closed"
        encounter.save()
        messages.success(request, "The visit has been finalized successfully.")
        return redirect(
            reverse("appointments:doctor_patient_overview", args=[encounter.patient.id])
        )

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
                | Q(id__icontains=query)
            )  # Properly close parentheses here
        ).values("id", "first_name", "last_name")
        return JsonResponse(list(patients), safe=False)
    return JsonResponse([], safe=False)


def some_view(request):
    # Ensure patient IDs are handled correctly
    patient = Patient.objects.get(id="12345")  # ExampleAdd Diagnosis usage
    
class PatientView(View):
    template_name = "appointments/patient_form.html"
    
    def get(self, request, patient_id=None):
        if patient_id:
            # Update or view a specific patient
            patient = get_object_or_404(Patient, id=patient_id)
            form = PatientForm(instance=patient)
            return render(request, self.template_name, {"form": form, "patient": patient})
        else:
            # List all patients
            patients = Patient.objects.all()
            return render(request, "appointments/patient_list.html", {"patients": patients})

    def posts(self,request,patient_id = None):
        if patient_id:
            patient = get_object_or_404(Patient, id=patient_id)
            form = PatientForm(request.POST, instance=patient)
            if form.is_valid():
                patient = form.save()
                updated_data = {
                    "resourceType": "Patient",
                    "name": [{"use": "official", "family": patient.full_name.split()[-1], "given": patient.full_name.split()[:-1]}],
                    "gender": patient.gender,
                    "birthDate": str(patient.dob),
                    "telecom": [{"system": "phone", "value": patient.contact}],
                }
                update_patient_in_cloud.delay(patient.id, updated_data)
                messages.success(request, "Patient updated successfully.")
                return redirect("patient_list")
        else:               
            form = PatientForm(request.POST)
            if form.is_valid():
                patient = form.save()
                resource_data = {
                    "resourceType": "Patient",
                    "name": [{"use": "official", "family": patient.full_name.split()[-1], "given": patient.full_name.split()[:-1]}],
                    "gender": patient.gender,
                    "birthDate": str(patient.dob),
                    "telecom": [{"system": "phone", "value": patient.contact}],
                }
                push_patient_to_cloud.delay(resource_data)
                messages.success(request, "Patient created successfully!")
                return redirect("patient_list")
        return render(request, self.template_name, {"form": form})
    
    def delete(self, request, patient_id):
        patient = get_object_or_404(Patient, id=patient_id)
        patient.delete()
        delete_patient_from_cloud.delay(patient_id)
        messages.success(request, "Patient deleted successfully!")
        return JsonResponse({"message": "Patient deleted successfully!"})
            

class EncounterView(View):
    template_name = "appointments/encounter_form.html"

    def get(self, request, encounter_id=None):
        if encounter_id:
            encounter = get_object_or_404(Encounter, id=encounter_id)
            form = EncounterForm(instance=encounter)
            return render(request, self.template_name, {"form": form, "encounter": encounter})
        else:
            encounters = Encounter.objects.all()
            return render(request, "appointments/encounter_list.html", {"encounters": encounters})

    def post(self, request, encounter_id=None):
        if encounter_id:
            encounter = get_object_or_404(Encounter, id=encounter_id)
            form = EncounterForm(request.POST, instance=encounter)
            if form.is_valid():
                encounter = form.save()
                updated_data = {
                    "resourceType": "Encounter",
                    "status": encounter.status,
                    "period": {
                        "start": str(encounter.start_time),
                        "end": str(encounter.end_time),
                    },
                    "subject": {"reference": f"Patient/{encounter.patient.id}"},
                    "participant": [{"individual": {"reference": f"Practitioner/{encounter.doctor.id}"}}],
                    "notes": encounter.notes,
                }
                update_encounter_in_cloud.delay(encounter.id, updated_data)
                messages.success(request, "Encounter updated successfully!")
                return redirect("encounter_list")
        else:
            form = EncounterForm(request.POST)
            if form.is_valid():
                encounter = form.save()
                resource_data = {
                    "resourceType": "Encounter",
                    "status": encounter.status,
                    "period": {
                        "start": str(encounter.start_time),
                        "end": str(encounter.end_time),
                    },
                    "subject": {"reference": f"Patient/{encounter.patient.id}"},
                    "participant": [{"individual": {"reference": f"Practitioner/{encounter.doctor.id}"}}],
                    "notes": encounter.notes,
                }
                push_encounter_to_cloud.delay(resource_data)
                messages.success(request, "Encounter created successfully!")
                return redirect("encounter_list")
        return render(request, self.template_name, {"form": form})

    def delete(self, request, encounter_id):
        encounter = get_object_or_404(Encounter, id=encounter_id)
        encounter.delete()
        delete_encounter_from_cloud.delay(encounter_id)
        messages.success(request, "Encounter deleted successfully!")
        return JsonResponse({"message": "Encounter deleted successfully!"})
    
class LabResultView(View):
    template_name = "appointments/lab_result_form.html"

    def get(self, request, lab_result_id=None):
        if lab_result_id:
            lab_result = get_object_or_404(LabResult, id=lab_result_id)
            form = LabResultForm(instance=lab_result)
            return render(request, self.template_name, {"form": form, "lab_result": lab_result})
        else:
            # List all lab results
            lab_results = LabResult.objects.all()
            return render(request, "appointments/lab_result_list.html", {"lab_results": lab_results})

    def post(self, request, lab_result_id=None):
        if lab_result_id:
            # Update an existing lab result
            lab_result = get_object_or_404(LabResult, id=lab_result_id)
            form = LabResultForm(request.POST, request.FILES, instance=lab_result)
            if form.is_valid():
                lab_result = form.save()
                # Prepare updated data for Google Cloud
                updated_data = {
                    "resourceType": "DiagnosticReport",
                    "status": lab_result.status,
                    "subject": {"reference": f"Patient/{lab_result.patient.id}"},
                    "encounter": {"reference": f"Encounter/{lab_result.encounter.id}"},
                    "code": {"text": lab_result.test_type},
                    "presentedForm": [{"url": lab_result.file.url}],
                }
                # Update in Google Cloud in the background
                update_lab_result_in_cloud.delay(lab_result.id, updated_data)
                messages.success(request, "Lab result updated successfully!")
                return redirect("lab_result_list")
        else:
            # Create a new lab result
            form = LabResultForm(request.POST, request.FILES)
            if form.is_valid():
                lab_result = form.save()
                # Prepare data for Google Cloud
                resource_data = {
                    "resourceType": "DiagnosticReport",
                    "status": lab_result.status,
                    "subject": {"reference": f"Patient/{lab_result.patient.id}"},
                    "encounter": {"reference": f"Encounter/{lab_result.encounter.id}"},
                    "code": {"text": lab_result.test_type},
                    "presentedForm": [{"url": lab_result.file.url}],
                }
                # Push to Google Cloud in the background
                push_lab_result_to_cloud.delay(resource_data)
                messages.success(request, "Lab result created successfully!")
                return redirect("lab_result_list")
        return render(request, self.template_name, {"form": form})

    def delete(self, request, lab_result_id):
        lab_result = get_object_or_404(LabResult, id=lab_result_id)
        lab_result.delete()
        # Delete from Google Cloud in the background
        delete_lab_result_from_cloud.delay(lab_result_id)
        messages.success(request, "Lab result deleted successfully!")
        return JsonResponse({"message": "Lab result deleted successfully!"})
    
class PrescriptionView(View):
    template_name = "#"

    def get(self, request, prescription_id=None):
        """Handle GET requests for listing, creating, or updating prescriptions."""
        if prescription_id:
            # Update or view a specific prescription
            prescription = get_object_or_404(Prescription, id=prescription_id)
            form = PrescriptionForm(instance=prescription)
            return render(request, self.template_name, {"form": form, "prescription": prescription})
        else:
            # List all prescriptions
            prescriptions = Prescription.objects.all()
            return render(request, "appointments/prescription_list.html", {"prescriptions": prescriptions})

    def post(self, request, prescription_id=None):
        """Handle POST requests for creating or updating prescriptions."""
        if prescription_id:
            # Update an existing prescription
            prescription = get_object_or_404(Prescription, id=prescription_id)
            form = PrescriptionForm(request.POST, instance=prescription)
            if form.is_valid():
                prescription = form.save()
                # Prepare updated data for Google Cloud
                updated_data = {
                    "resourceType": "MedicationRequest",
                    "status": "active",
                    "medicationCodeableConcept": {"text": prescription.medication_name},
                    "subject": {"reference": f"Patient/{prescription.patient.id}"},
                    "encounter": {"reference": f"Encounter/{prescription.encounter.id}"},
                    "dosageInstruction": [{"text": f"{prescription.dosage}, {prescription.duration}"}],
                    "requester": {"reference": f"Practitioner/{prescription.doctor.id}"},
                }
                # Update in Google Cloud in the background
                update_prescription_in_cloud.delay(prescription.id, updated_data)
                messages.success(request, "Prescription updated successfully!")
                return redirect("prescription_list")
        else:
            # Create a new prescription
            form = PrescriptionForm(request.POST)
            if form.is_valid():
                prescription = form.save()
                # Prepare data for Google Cloud
                resource_data = {
                    "resourceType": "MedicationRequest",
                    "status": "active",
                    "medicationCodeableConcept": {"text": prescription.medication_name},
                    "subject": {"reference": f"Patient/{prescription.patient.id}"},
                    "encounter": {"reference": f"Encounter/{prescription.encounter.id}"},
                    "dosageInstruction": [{"text": f"{prescription.dosage}, {prescription.duration}"}],
                    "requester": {"reference": f"Practitioner/{prescription.doctor.id}"},
                }
                # Push to Google Cloud in the background
                push_prescription_to_cloud.delay(resource_data)
                messages.success(request, "Prescription created successfully!")
                return redirect("prescription_list")
        return render(request, self.template_name, {"form": form})

    def delete(self, request, prescription_id):
        """Handle DELETE requests for deleting a prescription."""
        prescription = get_object_or_404(Prescription, id=prescription_id)
        prescription.delete()
        # Delete from Google Cloud in the background
        delete_prescription_from_cloud.delay(prescription_id)
        messages.success(request, "Prescription deleted successfully!")
        return JsonResponse({"message": "Prescription deleted successfully!"})

class ImmunizationView(View):
    template_name = "appointments/immunization_form.html"

    def get(self, request, immunization_id=None):
        """Handle GET requests for listing, creating, or updating immunizations."""
        if immunization_id:
            # Update or view a specific immunization
            immunization = get_object_or_404(Immunization, id=immunization_id)
            form = ImmunizationForm(instance=immunization)
            return render(request, self.template_name, {"form": form, "immunization": immunization})
        else:
            # List all immunizations
            immunizations = Immunization.objects.all()
            return render(request, "appointments/immunization_list.html", {"immunizations": immunizations})

    def post(self, request, immunization_id=None):
        """Handle POST requests for creating or updating immunizations."""
        if immunization_id:
            # Update an existing immunization
            immunization = get_object_or_404(Immunization, id=immunization_id)
            form = ImmunizationForm(request.POST, instance=immunization)
            if form.is_valid():
                immunization = form.save()
                # Prepare updated data for Google Cloud
                updated_data = {
                    "resourceType": "Immunization",
                    "status": immunization.status.lower(),
                    "vaccineCode": {"text": immunization.name},
                    "occurrenceDateTime": str(immunization.date),
                    "doseQuantity": {"text": immunization.dose},
                    "encounter": {"reference": f"Encounter/{immunization.encounter.id}"},
                }
                # Update in Google Cloud in the background
                update_immunization_in_cloud.delay(immunization.id, updated_data)
                messages.success(request, "Immunization updated successfully!")
                return redirect("immunization_list")
        else:
            # Create a new immunization
            form = ImmunizationForm(request.POST)
            if form.is_valid():
                immunization = form.save()
                # Prepare data for Google Cloud
                resource_data = {
                    "resourceType": "Immunization",
                    "status": immunization.status.lower(),
                    "vaccineCode": {"text": immunization.name},
                    "occurrenceDateTime": str(immunization.date),
                    "doseQuantity": {"text": immunization.dose},
                    "encounter": {"reference": f"Encounter/{immunization.encounter.id}"},
                }
                # Push to Google Cloud in the background
                push_immunization_to_cloud.delay(resource_data)
                messages.success(request, "Immunization created successfully!")
                return redirect("immunization_list")
        return render(request, self.template_name, {"form": form})

    def delete(self, request, immunization_id):
        """Handle DELETE requests for deleting an immunization."""
        immunization = get_object_or_404(Immunization, id=immunization_id)
        immunization.delete()
        # Delete from Google Cloud in the background
        delete_immunization_from_cloud.delay(immunization_id)
        messages.success(request, "Immunization deleted successfully!")
        return JsonResponse({"message": "Immunization deleted successfully!"})
    
class DocumentView(View):
    template_name = "#"

    def get(self, request, document_id=None):
        """Handle GET requests for listing, creating, or updating documents."""
        if document_id:
            # Update or view a specific document
            document = get_object_or_404(Document, id=document_id)
            form = DocumentForm(instance=document)
            return render(request, self.template_name, {"form": form, "document": document})
        else:
            # List all documents
            documents = Document.objects.all()
            return render(request, "appointments/document_list.html", {"documents": documents})

    def post(self, request, document_id=None):
        """Handle POST requests for creating or updating documents."""
        if document_id:
            # Update an existing document
            document = get_object_or_404(Document, id=document_id)
            form = DocumentForm(request.POST, request.FILES, instance=document)
            if form.is_valid():
                document = form.save()
                # Prepare updated data for Google Cloud
                updated_data = {
                    "resourceType": "DocumentReference",
                    "status": "current",
                    "type": {"text": document.doc_type},
                    "subject": {"reference": f"Patient/{document.patient.id}"},
                    "context": {"encounter": {"reference": f"Encounter/{document.encounter.id}"}},
                    "content": [{"attachment": {"url": document.file.url, "title": document.title}}],
                }
                # Update in Google Cloud in the background
                update_document_in_cloud.delay(document.id, updated_data)
                messages.success(request, "Document updated successfully!")
                return redirect("document_list")
        else:
            # Create a new document
            form = DocumentForm(request.POST, request.FILES)
            if form.is_valid():
                document = form.save()
                # Prepare data for Google Cloud
                resource_data = {
                    "resourceType": "DocumentReference",
                    "status": "current",
                    "type": {"text": document.doc_type},
                    "subject": {"reference": f"Patient/{document.patient.id}"},
                    "context": {"encounter": {"reference": f"Encounter/{document.encounter.id}"}},
                    "content": [{"attachment": {"url": document.file.url, "title": document.title}}],
                }
                # Push to Google Cloud in the background
                push_document_to_cloud.delay(resource_data)
                messages.success(request, "Document created successfully!")
                return redirect("document_list")
        return render(request, self.template_name, {"form": form})

    def delete(self, request, document_id):
        """Handle DELETE requests for deleting a document."""
        document = get_object_or_404(Document, id=document_id)
        document.delete()
        # Delete from Google Cloud in the background
        delete_document_from_cloud.delay(document_id)
        messages.success(request, "Document deleted successfully!")
        return JsonResponse({"message": "Document deleted successfully!"})
    
class MedicalRecordsView(View):
    template_name = "#"

    def get(self, request, record_id=None):
        """Handle GET requests for listing, creating, or updating medical records."""
        if record_id:
            # Update or view a specific medical record
            record = get_object_or_404(MedicalRecords, id=record_id)
            form = MedicalRecordsForm(instance=record)
            return render(request, self.template_name, {"form": form, "record": record})
        else:
            # List all medical records
            records = MedicalRecords.objects.all()
            return render(request, "appointments/medical_records_list.html", {"records": records})

    def post(self, request, record_id=None):
        """Handle POST requests for creating or updating medical records."""
        if record_id:
            # Update an existing medical record
            record = get_object_or_404(MedicalRecords, id=record_id)
            form = MedicalRecordsForm(request.POST, request.FILES, instance=record)
            if form.is_valid():
                form.save()
                messages.success(request, "Medical record updated successfully!")
                return redirect("medical_records_list")
        else:
            # Create a new medical record
            form = MedicalRecordsForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Medical record created successfully!")
                return redirect("medical_records_list")
        return render(request, self.template_name, {"form": form})

    def delete(self, request, record_id):
        """Handle DELETE requests for deleting a medical record."""
        record = get_object_or_404(MedicalRecords, id=record_id)
        record.delete()
        messages.success(request, "Medical record deleted successfully!")
        return JsonResponse({"message": "Medical record deleted successfully!"})