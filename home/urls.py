from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("starter/", views.starter, name="starter"),
    path("chatbot/", views.chatbot, name="chatbot"),
    path('calendar/', views.calendar_view, name='calendar'),
    path('appointments/api/', views.get_appointments, name='appointments_api'),
]
