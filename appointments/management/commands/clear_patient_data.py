from django.core.management.base import BaseCommand
from appointments.models import Encounter, LabResult, Prescription, Document, Diagnosis, Medication, Immunization

class Command(BaseCommand):
    help = "Clear all patient-related data for the Patient Overview"

    def handle(self, *args, **kwargs):
        # Clear all related models
        Encounter.objects.all().delete()
        LabResult.objects.all().delete()
        Prescription.objects.all().delete()
        Document.objects.all().delete()
        Diagnosis.objects.all().delete()
        Medication.objects.all().delete()
        Immunization.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Successfully cleared all patient-related data."))
