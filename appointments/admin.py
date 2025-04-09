from django.contrib import admin
from .models import Appointment, MedicalRecords, Patient, Encounter, Immunization, LabResult, Prescription, Document

admin.site.register(Patient)
admin.site.register(Appointment)
admin.site.register(Encounter)
admin.site.register(Immunization)
admin.site.register(LabResult)
admin.site.register(Prescription)
admin.site.register(Document)
admin.site.register(MedicalRecords)
