from datetime import datetime, date
from .models import Appointment


def inbox_data(request):
    # ...existing code (if any)...

    if not request.user.is_authenticated:
        return {}

    today = date.today()
    user = request.user
    is_doctor = user.groups.filter(name="Doctor").exists()
    is_patient = user.groups.filter(name="Patient").exists()

    if is_patient:
        upcoming_appointments = Appointment.objects.filter(
            patient=request.user, date__date__gte=today
        ).select_related("doctor", "patient")
    elif is_doctor:
        upcoming_appointments = Appointment.objects.filter(
            doctor=request.user, date__date__gte=today
        ).select_related("doctor", "patient")
    else:
        upcoming_appointments = Appointment.objects.filter(
            date__date__gte=today
        ).select_related("doctor", "patient")

    # If doctor, show same-day appointment count
    same_day_count = (
        upcoming_appointments.filter(date__date=today).count() if is_doctor else 0
    )

    return {
        "inbox_appointments": upcoming_appointments[:5],  # limit to 5 if you wish
        "inbox_none": upcoming_appointments.count() == 0,
        "today_app_count": same_day_count,
        "is_doctor": is_doctor,
        "is_patient": is_patient,
    }
