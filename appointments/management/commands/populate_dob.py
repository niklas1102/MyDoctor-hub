from django.core.management.base import BaseCommand
from appointments.models import Patient
from datetime import date
import random

class Command(BaseCommand):
    help = 'Populate DOB for existing patients'

    def handle(self, *args, **kwargs):
        patients = Patient.objects.filter(dob__isnull=True)
        for patient in patients:
            # Assign a random DOB between 1950 and 2005
            year = random.randint(1950, 2005)
            month = random.randint(1, 12)
            day = random.randint(1, 28)  # Avoid invalid dates
            patient.dob = date(year, month, day)
            patient.save()
        self.stdout.write(self.style.SUCCESS('Successfully populated DOB for existing patients.'))
