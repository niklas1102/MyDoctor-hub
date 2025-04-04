# home/urls.py

from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("starter/", views.starter, name="starter"),
    path("chatbot/", views.chatbot, name="chatbot"),
    path("appointments/", include("appointments.urls", namespace="appointments")),
    path("inbox/", views.inbox, name="inbox"),
]
