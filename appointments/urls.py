# appointments/urls.py

from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_list, name='appointment_list'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('doctor/', views.doctor_appointments, name='doctor_appointments'),
    path('doctor/calendar/', views.doctor_calendar, name='doctor_calendar'),
]
