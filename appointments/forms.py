# appointments/forms.py

from django import forms
from .models import Appointment, Diagnosis, Document, Immunization, LabResult, MedicalRecords, Patient, Encounter, Prescription
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Div, HTML, Field
from datetime import datetime

User = get_user_model()

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['full_name', 'dob', 'gender', 'contact']

class EncounterForm(forms.ModelForm):
    class Meta:
        model = Encounter
        fields = ['start_time', 'end_time', 'status', 'doctor', 'patient', 'notes']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
class LabResultForm(forms.ModelForm):
    class Meta:
        model = LabResult
        fields = ['encounter', 'patient', 'test_type', 'status', 'file']
        
class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['encounter', 'patient', 'medication_name', 'dosage', 'duration', 'doctor']
        
class DiagnosisForm(forms.ModelForm):
    class Meta:
        model = Diagnosis
        fields = ['encounter', 'description']
        
class ImmunizationForm(forms.ModelForm):
    class Meta:
        model = Immunization
        fields = ['encounter', 'name', 'date', 'dose', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }



class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['encounter', 'patient', 'title', 'doc_type', 'file']
        
class AppointmentForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name="Doctor").exclude(
            first_name="", last_name=""
        ),  # Exclude doctors without names
        widget=forms.Select(attrs={"class": "form-control"}),
        empty_label="Select Doctor",
    )

    class Meta:
        model = Appointment
        fields = ["doctor", "date", "reason"]
        widgets = {
            "date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget = forms.HiddenInput()  # Now handled by modal
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("doctor", css_class="mb-4"),
            HTML("""<button id="openCalendar" type="button" class="mt-2 px-4 py-2 bg-blue-100 text-blue-600 rounded-md hover:bg-blue-200">
                <i class="far fa-calendar-alt mr-2"></i> Select Date & Time
            </button>"""),
            Field("date", css_class="mb-4 hidden"),  # Hidden field
            Field("reason", css_class="mb-4"),
        )
        self.helper.add_input(
            Submit("submit", "Book Appointment", css_class="submit-button")
        )

    def clean_doctor(self):
        doctor = self.cleaned_data.get("doctor")
        if not doctor:
            raise forms.ValidationError("Please select a valid doctor.")
        return doctor

class MedicalRecordsForm(forms.ModelForm):
    class Meta:
        model = MedicalRecords
        fields = ['encounter', 'patient', 'record_type', 'type', 'summary', 'file']
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 4}),
        }
        
