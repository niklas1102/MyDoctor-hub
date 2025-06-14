from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from appointments.models import LabResult, Encounter
from datetime import datetime, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = "Add test lab results for Brenda Akello"

    def handle(self, *args, **kwargs):
        # Fetch Brenda Akello's user record
        try:
            brenda = User.objects.get(first_name="Brenda", last_name="Akello")
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("User Brenda Akello not found."))
            return

        # Remove old lab results for Brenda
        LabResult.objects.filter(patient=brenda).delete()

        # Ensure a unique encounter for Brenda
        encounter = Encounter.objects.filter(patient=brenda).first()
        if not encounter:
            encounter = Encounter.objects.create(
                patient=brenda,
                doctor=None,
                status="Open",
                notes="Test encounter for lab results"
            )

        # Add test lab results with different dates in the past
        today = datetime(2025, 4, 14)  # Fixed today's date for consistency
        lab_results_data = [
            {"test_type": "Blood Test", "status": "Completed", "date": today - timedelta(days=10)},
            {"test_type": "X-Ray", "status": "Pending", "date": today - timedelta(days=20)},
            {"test_type": "MRI Scan", "status": "In Progress", "date": today - timedelta(days=30)},
        ]

        for lab_data in lab_results_data:
            LabResult.objects.create(
                encounter=encounter,
                patient=brenda,
                test_type=lab_data["test_type"],
                status=lab_data["status"],
                date=lab_data["date"],
            )

        self.stdout.write(self.style.SUCCESS("Old lab results removed and new test lab results added for Brenda Akello with correct past dates."))
