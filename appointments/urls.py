# appointments/urls.py

from django.urls import path
from . import views
from .views import doctor_patient_lookup

app_name = "appointments"

urlpatterns = [
    path("", views.appointment_list, name="appointment_list"),
    path("book/", views.book_appointment, name="book_appointment"),
    path(
        "cancel/<int:appointment_id>/",
        views.cancel_appointment,
        name="cancel_appointment",
    ),
    path("doctor/", views.doctor_appointments, name="doctor_appointments"),
    path("doctor/calendar/", views.doctor_calendar, name="doctor_calendar"),
    path("doctor/patients/", views.doctor_patient_lookup, name="doctor_patient_lookup"),
    path(
        "doctor/patient/<int:patient_id>/",
        views.doctor_patient_overview,
        name="doctor_patient_overview",
    ),
    path(
        "doctor/encounter/<int:encounter_id>/",
        views.doctor_encounter_view,
        name="doctor_encounter_view",
    ),
    path("doctor/search-patients/", views.search_patients, name="search_patients"),
]
