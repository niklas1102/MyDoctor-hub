# appointments/forms.py

from django import forms
from .models import Appointment
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field

User = get_user_model()

class AppointmentForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name='Doctor').exclude(first_name='', last_name=''),  # Exclude doctors without names
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Doctor"
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'reason']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            
            Field('doctor', css_class='mb-4'),
            Field('date', css_class='mb-4'),
            Field('reason', css_class='mb-4'),
        )
        self.helper.add_input(Submit('submit', 'Book Appointment', css_class='bg-blue-500'))

    def clean_doctor(self):
        doctor = self.cleaned_data.get('doctor')
        if not doctor:
            raise forms.ValidationError("Please select a valid doctor.")
        return doctor