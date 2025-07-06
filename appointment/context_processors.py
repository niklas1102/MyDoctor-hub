# appointment/context_processors.py

from django.contrib.auth.models import User
from .models import Appointment, StaffMember


def appointment_data(request):
    """
    Context processor to provide appointment-related data to templates.
    """
    context = {
        'is_doctor': False,
        'is_patient': False,
        'is_staff_member': False,
    }
    
    if request.user.is_authenticated:
        # Check if user is a doctor (staff member in new appointment system)
        try:
            staff_member = StaffMember.objects.get(user=request.user)
            context['is_doctor'] = True
            context['is_staff_member'] = True
            context['staff_member'] = staff_member
        except StaffMember.DoesNotExist:
            # Check if user is in Doctor group (legacy system)
            context['is_doctor'] = request.user.groups.filter(name="Doctor").exists()
            context['is_patient'] = request.user.groups.filter(name="Patient").exists()
    
    return context
