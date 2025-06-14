from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from appointments.models import Immunization, Encounter
from datetime import datetime, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = "Add test immunizations for Brenda Akello"

    def handle(self, *args, **kwargs):
        # Fetch Brenda Akello's user record
        try:
            brenda = User.objects.get(first_name="Brenda", last_name="Akello")
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("User Brenda Akello not found."))
            return

        # Remove old immunizations for Brenda
        Immunization.objects.filter(encounter__patient=brenda).delete()

        # Ensure a unique encounter for Brenda
        encounter = Encounter.objects.filter(patient=brenda).first()
        if not encounter:
            encounter = Encounter.objects.create(
                patient=brenda,
                doctor=None,
                status="Open",
                notes="Test encounter for immunizations"
            )

        # Add test immunizations
        immunizations_data = [
            {"vaccine": "Yellow Fever", "date": datetime(2025, 4, 1), "dose": "1st Dose", "status": "Completed"},
            {"vaccine": "Hepatitis B", "date": datetime(2025, 3, 20), "dose": "2nd Dose", "status": "Completed"},
            {"vaccine": "COVID-19", "date": datetime(2025, 3, 10), "dose": "Booster", "status": "Completed"},
            {"vaccine": "Tetanus", "date": datetime(2025, 2, 25), "dose": "1st Dose", "status": "Scheduled"},
        ]

        for immunization_data in immunizations_data:
            Immunization.objects.create(
                encounter=encounter,
                name=immunization_data["vaccine"],
                date=immunization_data["date"],
                dose=immunization_data["dose"],
                status=immunization_data["status"],
            )

        self.stdout.write(self.style.SUCCESS("Old immunizations removed and new test immunizations added for Brenda Akello."))
