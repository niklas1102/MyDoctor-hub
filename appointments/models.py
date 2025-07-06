# appointments/models.py

import random
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class Patient(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]
    id = models.CharField(
        max_length=5, primary_key=True, unique=True, editable=False, default=None
    )
    temp_id = models.CharField(
        max_length=5, null=True, unique=True
    )  # Temporary field for migration
    full_name = models.CharField(max_length=255, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)  # Add date of birth field
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)  # Fixed gender field
    contact = models.CharField(max_length=255, null=True, blank=True)   
    
    def save(self, *args, **kwargs):
        if not self.id:  # Generate a random ID only if the ID is not already set
            self.id = self.generate_random_id()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_random_id():
        while True:
            random_id = f"{random.randint(10000, 99999)}"
            if not Patient.objects.filter(id=random_id).exists():
                return random_id
    

class Appointment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("canceled", "Canceled"),
    ]
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="appointments_as_doctor",
        on_delete=models.CASCADE,
    )
    patient = models.ForeignKey(
        User, related_name="patient_appointments", on_delete=models.CASCADE
    )
    date = models.DateTimeField()
    reason = models.CharField(max_length=255, default="No reason provided")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    meeting_room_id = models.CharField(max_length=100, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.meeting_room_id:
            self.meeting_room_id = self.generate_meeting_room_id()
        super().save(*args, **kwargs)

    def generate_meeting_room_id(self):
        """Generate a unique meeting room ID for Jitsi Meet"""
        while True:
            # Use a very simple format that doesn't trigger authentication
            import string
            import random
            # Generate a simple alphanumeric room name
            room_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
            if not Appointment.objects.filter(meeting_room_id=room_id).exists():
                return room_id

    def __str__(self):
        return f"Appointment with Dr. {self.doctor.last_name} on {self.date.strftime('%Y-%m-%d %H:%M')}"


class Encounter(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(null = True, blank=True)
    end_time = models.DateTimeField(null = True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[("Active", "Active"), ("Finished", "Finished")],
        default="Active",
    )
    doctor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="doctor_encounters"
    )
    patient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="patient_encounters"
    )
    reason = models.TextField(default="No reason provided")
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Encounter on {self.date} - {self.status}"


class LabResult(models.Model):
    encounter = models.ForeignKey(
        Encounter, on_delete=models.CASCADE, related_name="labresults", null=True
    )
    patient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="lab_results"
    )
    test_type = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default="Pending")
    date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(
        upload_to="lab_results/", null=True, blank=True
    )  # Ensure this field exists

    def __str__(self):
        return f"{self.test_type} - {self.status} ({self.date.strftime('%Y-%m-%d')})"


class Prescription(models.Model):
    encounter = models.ForeignKey(
        Encounter, on_delete=models.CASCADE, related_name="prescriptions", null=True
    )
    patient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="prescriptions", null=True
    )
    medication_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=255)
    duration = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    doctor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="issued_prescriptions", null=True
    )

    def __str__(self):
        return f"{self.medication_name} prescribed by Dr. {self.doctor.last_name} on {self.date.strftime('%Y-%m-%d')}"


class Document(models.Model):
    encounter = models.ForeignKey(
        Encounter, on_delete=models.CASCADE, related_name="documents", null=True
    )
    patient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="documents", null=True
    )
    title = models.CharField(max_length=255)
    doc_type = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(
        upload_to="documents/", default="documents/default-file.txt"
    )  # Added default value

    def __str__(self):
        return f"{self.title} ({self.doc_type}) uploaded on {self.upload_date.strftime('%Y-%m-%d')}"


class Diagnosis(models.Model):
    encounter = models.ForeignKey(
        Encounter, on_delete=models.CASCADE, related_name="diagnoses", null=True
    )
    description = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Diagnosis: {self.description[:50]} (Encounter ID: {self.encounter.id})"


class Medication(models.Model):
    encounter = models.ForeignKey(
        Encounter, on_delete=models.CASCADE, related_name="medications", null=True
    )
    name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=255)
    duration = models.CharField(max_length=255)
    date_prescribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Medication: {self.name} (Encounter ID: {self.encounter.id})"


class Immunization(models.Model):
    encounter = models.ForeignKey(
        Encounter, on_delete=models.CASCADE, related_name="immunizations", null=True
    )
    name = models.CharField(max_length=255)
    date = models.DateField()
    dose = models.CharField(max_length=255)
    status = models.CharField(
        max_length=50,
        choices=[
            ("Completed", "Completed"),
            ("Scheduled", "Scheduled"),
            ("Missed", "Missed"),
        ],
    )

    def __str__(self):
        return f"Immunization: {self.name} (Encounter ID: {self.encounter.id})"

class MedicalRecords(models.Model):
    encounter = models.ForeignKey(
        Encounter, on_delete=models.CASCADE, related_name="medical_records", null=True
    )
    patient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="medical_records", null=True
    )
    record_type = models.CharField(max_length=255)
    type = models.CharField(
        max_length=50,
        choices=[
            ("Diagnosis", "Diagnosis"),
            ("Medication", "Medication"),
            ("Immunization", "Immunization"),
            ("Lab Result", "Lab Result"),
            ("Prescription", "Prescription"),
            ("Document", "Document"),
        ],
    )
    summary = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="medical_records/", null=True, blank=True)

    def __str__(self):
        return f"{self.record_type} - {self.date.strftime('%Y-%m-%d')}"