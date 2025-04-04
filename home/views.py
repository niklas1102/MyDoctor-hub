from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime, timedelta

from .models import *


@login_required(login_url="/users/signin/")
def index(request):

    context = {
        "segment": "dashboard",
    }
    return render(request, "dashboard/index.html", context)


@login_required(login_url="/users/signin/")
def starter(request):

    context = {}
    return render(request, "pages/starter.html", context)


@login_required(login_url="/users/signin/")
def chatbot(request):
    context = {
        "segment": "chatbot",
    }
    return render(request, "dashboard/chatbot.html", context)


def calendar_view(request):
    context = {"segment": "appointments"}
    return render(request, "appointments/calendar.html", context)


def calendar_view(request):
    context = {"segment": "appointments"}
    return render(request, "appointments/calendar.html", context)


@login_required(login_url="/users/signin/")
def inbox(request):
    context = {
        "segment": "inbox",
    }
    return render(request, "dashboard/inbox.html", context)


def get_appointments(request):
    # Example data for appointments (Replace with actual DB data)
    events = [
        {
            "id": 1,
            "title": "Doctor Appointment",
            "start": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),  # Full timestamp
            "end": (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S"),
        },
        {
            "id": 2,
            "title": "Follow-up Visit",
            "start": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S"),
            "end": (datetime.now() + timedelta(days=2, hours=1)).strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),
        },
    ]
    return JsonResponse(events, safe=False)


def terms_view(request):
    return render(request, "pages/terms.html")


def privacy_view(request):
    return render(request, "pages/privacy.html")


def licensing_view(request):
    return render(request, "pages/licensing.html")


def cookie_view(request):
    return render(request, "pages/cookie.html")


def contact_view(request):
    return render(request, "pages/contact.html")
