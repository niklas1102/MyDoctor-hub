from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from appointments.models import Prescription, Encounter
from datetime import datetime, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = "Add test prescriptions for Brenda Akello"

    def handle(self, *args, **kwargs):
        # Fetch Brenda Akello's user record
        try:
            brenda = User.objects.get(first_name="Brenda", last_name="Akello")
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("User Brenda Akello not found."))
            return

        # Remove old prescriptions for Brenda
        Prescription.objects.filter(patient=brenda).delete()

        # Ensure a unique encounter for Brenda
        encounter = Encounter.objects.filter(patient=brenda).first()
        if not encounter:
            encounter = Encounter.objects.create(
                patient=brenda,
                doctor=None,
                status="Open",
                notes="Test encounter for prescriptions"
            )

        # Add test prescriptions
        prescriptions_data = [
            {"medication_name": "Amoxicillin", "dosage": "500mg twice daily", "duration": "7 days"},
            {"medication_name": "Ibuprofen", "dosage": "200mg every 6 hours", "duration": "5 days"},
            {"medication_name": "Metformin", "dosage": "1000mg daily", "duration": "30 days"},
            {"medication_name": "Lisinopril", "dosage": "10mg daily", "duration": "90 days"},
        ]

        for prescription_data in prescriptions_data:
            Prescription.objects.create(
                encounter=encounter,
                patient=brenda,
                doctor=encounter.doctor,  # Use the encounter's doctor if available
                medication_name=prescription_data["medication_name"],
                dosage=prescription_data["dosage"],
                duration=prescription_data["duration"],
            )

        self.stdout.write(self.style.SUCCESS("Old prescriptions removed and new test prescriptions added for Brenda Akello."))
