from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from appointments.models import Encounter
from datetime import datetime

User = get_user_model()

class Command(BaseCommand):
    help = "Add test past visits for Brenda Akello"

    def handle(self, *args, **kwargs):
        # Fetch Brenda Akello's user record
        try:
            brenda = User.objects.get(first_name="Brenda", last_name="Akello")
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("User Brenda Akello not found."))
            return

        # Fetch or create doctors
        doctor_data = [
            {"first_name": "John", "last_name": "Doe"},
            {"first_name": "Jane", "last_name": "Smith"},
            {"first_name": "Emily", "last_name": "White"},
            {"first_name": "Mark", "last_name": "Brown"},
        ]
        doctors = {}
        for data in doctor_data:
            doctor, _ = User.objects.get_or_create(
                first_name=data["first_name"],
                last_name=data["last_name"],
                defaults={"username": f"{data['first_name']}{data['last_name']}".lower(), "email": f"{data['first_name'].lower()}.{data['last_name'].lower()}@example.com"}
            )
            doctors[f"{data['first_name']} {data['last_name']}"] = doctor

        # Remove old encounters (past visits) for Brenda
        Encounter.objects.filter(patient=brenda).delete()

        # Add test past visits
        past_visits_data = [
            {"date": datetime(2024, 5, 10), "doctor": doctors["John Doe"], "reason": "Routine Checkup", "notes": "All vitals normal."},
            {"date": datetime(2023, 11, 15), "doctor": doctors["Jane Smith"], "reason": "Flu Symptoms", "notes": "Prescribed antiviral medication."},
            {"date": datetime(2023, 7, 20), "doctor": doctors["Emily White"], "reason": "Back Pain", "notes": "Recommended physiotherapy."},
            {"date": datetime(2023, 3, 5), "doctor": doctors["Mark Brown"], "reason": "Allergy Consultation", "notes": "Prescribed antihistamines."},
        ]

        for visit_data in past_visits_data:
            Encounter.objects.create(
                patient=brenda,
                doctor=visit_data["doctor"],
                date=visit_data["date"],
                reason=visit_data["reason"],
                notes=visit_data["notes"],
                status="Closed",
            )

        self.stdout.write(self.style.SUCCESS("Old past visits removed and new test past visits added for Brenda Akello."))
