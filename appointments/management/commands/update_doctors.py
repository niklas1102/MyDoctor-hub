from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Update doctor records with first_name and last_name"

    def handle(self, *args, **kwargs):
        doctors = User.objects.filter(groups__name="Doctor")
        for doctor in doctors:
            if not doctor.first_name:
                doctor.first_name = "DefaultFirstName"  # Replace with actual first name
            if not doctor.last_name:
                doctor.last_name = "DefaultLastName"  # Replace with actual last name
            doctor.save()
            self.stdout.write(
                self.style.SUCCESS(f"Successfully updated doctor: {doctor.username}")
            )
