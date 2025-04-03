
from datetime import datetime, date
from .models import Appointment

def inbox_data(request):
    # ...existing code (if any)...

    if not request.user.is_authenticated:
        return {}

    today = date.today()
    user = request.user
    is_doctor = user.groups.filter(name='Doctor').exists()
    is_patient = user.groups.filter(name='Patient').exists()

    # Upcoming appointments (future or same day)
    upcoming_appointments = Appointment.objects.filter(
        doctor=user if is_doctor else None,
        date__date__gte=today
    ) if is_doctor else Appointment.objects.filter(
        patient=user, date__date__gte=today
    )

    upcoming_appointments = Appointment.objects.all()

    # If doctor, show same-day appointment count
    same_day_count = (
        upcoming_appointments.filter(date__date=today).count() if is_doctor else 0
    )

    return {
        'inbox_appointments': upcoming_appointments[:5],  # limit to 5 if you wish
        'inbox_none': upcoming_appointments.count() == 0,
        'today_app_count': same_day_count,
        'is_doctor': is_doctor,
        'is_patient': is_patient,
    }