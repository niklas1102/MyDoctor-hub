from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from appointments.models import LabResult, Prescription, Immunization, Encounter
from datetime import datetime, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = "Add test data for Brenda Akello, including lab results, prescriptions, immunizations, and past visits."

    def handle(self, *args, **kwargs):
        # Fetch Brenda Akello's user record
        try:
            brenda = User.objects.get(first_name="Brenda", last_name="Akello")
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("User Brenda Akello not found."))
            return

        # Remove old data
        LabResult.objects.filter(patient=brenda).delete()
        Prescription.objects.filter(patient=brenda).delete()
        Immunization.objects.filter(encounter__patient=brenda).delete()
        Encounter.objects.filter(patient=brenda).delete()

        # Ensure doctors exist
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

        # Add test lab results
        today = datetime(2025, 4, 14)
        lab_results_data = [
            {"test_type": "Blood Test", "status": "Completed", "date": today - timedelta(days=10)},
            {"test_type": "X-Ray", "status": "Pending", "date": today - timedelta(days=20)},
            {"test_type": "MRI Scan", "status": "In Progress", "date": today - timedelta(days=30)},
        ]
        encounter = Encounter.objects.create(
            patient=brenda,
            doctor=doctors["John Doe"],  # Assign a valid doctor
            status="Open",
            notes="Test encounter for lab results"
        )
        for lab_data in lab_results_data:
            LabResult.objects.create(
                encounter=encounter,
                patient=brenda,
                test_type=lab_data["test_type"],
                status=lab_data["status"],
                date=lab_data["date"],
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
                doctor=encounter.doctor,
                medication_name=prescription_data["medication_name"],
                dosage=prescription_data["dosage"],
                duration=prescription_data["duration"],
            )

        # Add test immunizations
        immunizations_data = [
            {"vaccine": "Yellow Fever", "date": today - timedelta(days=13), "dose": "1st Dose", "status": "Completed"},
            {"vaccine": "Hepatitis B", "date": today - timedelta(days=23), "dose": "2nd Dose", "status": "Completed"},
            {"vaccine": "COVID-19", "date": today - timedelta(days=33), "dose": "Booster", "status": "Completed"},
            {"vaccine": "Tetanus", "date": today - timedelta(days=43), "dose": "1st Dose", "status": "Scheduled"},
        ]
        for immunization_data in immunizations_data:
            Immunization.objects.create(
                encounter=encounter,
                name=immunization_data["vaccine"],
                date=immunization_data["date"],
                dose=immunization_data["dose"],
                status=immunization_data["status"],
            )

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

        self.stdout.write(self.style.SUCCESS("Test data added for Brenda Akello, including lab results, prescriptions, immunizations, and past visits."))
