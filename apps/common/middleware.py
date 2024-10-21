from django.shortcuts import redirect
from django.conf import settings

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and request.path not in [settings.LOGIN_URL, '/users/signup/']:
            return redirect(settings.LOGIN_URL)  # Redirect to login if not authenticated
        return self.get_response(request)
