from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import (
    LoginView,
    PasswordResetView,
    PasswordChangeView,
    PasswordResetConfirmView,
)
from django.views.generic import CreateView
from appointments.models import Encounter, Immunization, LabResult, Prescription, MedicalRecords
from appointments.tasks import push_patient_to_cloud
from apps.common.models import Product
from apps.users.models import Profile, Document  # Move the import to the top
from apps.users.forms import (
    SigninForm,
    SignupForm,
    UserPasswordChangeForm,
    UserSetPasswordForm,
    UserPasswordResetForm,
    ProfileForm,
)
from django.contrib.auth import logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib.auth import login
from apps.users.utils import user_filter
from django.contrib.auth.decorators import login_required
from django.apps import apps

# Create your views here.


@login_required(login_url="/users/signin/")
def index(request):

    prodName = ""

    if len(Product.objects.all()):
        prodName = Product.objects.all()[0].name

    return HttpResponse("INDEX Users" + " " + prodName)


class SignInView(LoginView):
    form_class = SigninForm
    template_name = "authentication/sign-in.html"


class SignUpView(CreateView):
    form_class = SignupForm
    template_name = "authentication/sign-up.html"
    success_url = "/users/signin/"  # Redirect after successful signup

    def form_valid(self, form):
        user = form.save()  # Save the new user
        login(self.request, user)
        
    
        if user.groups.filter(name="Patient").exists():
            resource_data = {
                "resourceType": "Patient",
                "id": str(user.uuid),  # Use the UUID as the FHIR ID
                "name": [{"use": "official", "family": user.last_name, "given": [user.first_name]}],
                "gender": user.profile.gender if hasattr(user, "profile") else "unknown",
                "birthDate": user.profile.birth_date.isoformat() if hasattr(user, "profile") and user.profile.birth_date else None,
            }

            push_patient_to_cloud.delay(resource_data)

        return super().form_valid(form)

    def form_invalid(self, form):
        # Print errors in the console for debugging
        print(form.errors)
        return super().form_invalid(form)


class UserPasswordChangeView(PasswordChangeView):
    template_name = "authentication/password-change.html"
    form_class = UserPasswordChangeForm


class UserPasswordResetView(PasswordResetView):
    template_name = "authentication/forgot-password.html"
    form_class = UserPasswordResetForm
    success_url = "/users/password-reset-done/"  # Add success URL


class UserPasswrodResetConfirmView(PasswordResetConfirmView):
    template_name = "authentication/reset-password.html"
    form_class = UserSetPasswordForm
    success_url = "/users/password-reset-complete/"  # Add success URL


def signout_view(request):
    logout(request)
    return redirect(reverse("signin"))


@login_required(login_url="/users/signin/")
def profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    documents = Document.objects.filter(user=request.user).order_by(
        "-upload_date"
    )  # Query documents for the logged-in user

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)

        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
    else:
        form = ProfileForm(instance=profile)

    # --- add these two lines so the template’s <input> and <select> have data-field from the start ---
    form.fields['date_of_birth'].widget.attrs.update({
        'data-field':'date_of_birth', 
        'id':'id_date_of_birth'
    })
    form.fields['gender'].widget.attrs.update({'data-field':'gender', 'id':'id_gender'})
    # ---------------------------------------------------------------------------

    user = request.user
    encounters = Encounter.objects.filter(patient=user).order_by("-date")
    lab_results = LabResult.objects.filter(patient=user).order_by("-date")
    prescriptions = Prescription.objects.filter(patient=user).order_by("-date")
    immunizations = Immunization.objects.filter(encounter__patient=user).order_by("-date")
    medical_records = MedicalRecords.objects.filter(patient=user).order_by("-date")

    context = {
        "form": form,
        "segment": "profile",
        "documents": documents,
        "past_visits": encounters,
        "lab_results": lab_results,
        "medications": prescriptions,
        "immunizations": immunizations,
        "medical_records": medical_records,
    }
    return render(request, "dashboard/profile.html", context)


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


@login_required
@require_POST
def update_profile_field(request):
    field = request.POST.get('field')
    value = request.POST.get('value')
    
    try:
        if field in ['first_name', 'last_name', 'email']:
            # Update User model fields
            setattr(request.user, field, value)
            request.user.save()
        else:
            # Update Profile model fields
            profile = request.user.profile
            # Handle special fields
            if field == 'pre_existing_conditions':
                # Convert to comma-separated string
                conditions = [c.strip() for c in value.split(',') if c.strip()]
                setattr(profile, field, ','.join(conditions))
            elif field == 'budget':
                # Convert to integer
                setattr(profile, field, int(value))
            elif field == 'date_of_birth':
                from datetime import datetime
                dob = datetime.strptime(value, '%Y-%m-%d').date()
                setattr(profile, field, dob)
            else:
                setattr(profile, field, value)
            profile.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
# @login_required
# @require_POST
# def update_profile_field(request):
#     field = request.POST.get('field')
#     value = request.POST.get('value')
    
#     try:
#         if field in ['first_name', 'last_name', 'email']:
#             setattr(request.user, field, value)
#             request.user.save()
#         else:
#             profile = request.user.profile
#             if field == 'pre_existing_conditions':
#                 setattr(profile, field, value)
#             elif field == 'gender':
#                 setattr(profile, field, value)
#             else:
#                 setattr(profile, field, value)
#             profile.save()
        
#         return JsonResponse({'success': True})
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)})
    
@login_required(login_url="/users/signin/")
def upload_avatar(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == "POST":
        profile.avatar = request.FILES.get("avatar")
        profile.save()
        messages.success(request, "Avatar uploaded successfully")
    return redirect(request.META.get("HTTP_REFERER"))


# @login_required(login_url="/users/signin/")
# def change_password(request):
#     user = request.user
#     if request.method == "POST":
#         if check_password(request.POST.get("current_password"), user.password):
#             user.set_password(request.POST.get("new_password"))
#             user.save()
#             messages.success(request, "Password changed successfully")
#         else:
#             messages.error(request, "Password doesn't match!")
#     return redirect(request.META.get("HTTP_REFERER"))

from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


@login_required
def change_password(request):
    if request.method == 'POST':
        print(request.POST)
        if request.POST.get("new_password") == request.POST.get("confirm_password"):
            user = request.user
            user.set_password(request.POST.get("new_password"))
            user.save()
            return JsonResponse({'success': True, 'message': 'Password changed successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Passwords do not match'})


    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


def user_list(request):
    filters = user_filter(request)
    user_list = User.objects.filter(**filters)
    form = SignupForm()

    page = request.GET.get("page", 1)
    paginator = Paginator(user_list, 5)
    users = paginator.page(page)

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            return post_request_handling(request, form)

    context = {
        "users": users,
        "form": form,
    }
    return render(request, "apps/users.html", context)


@login_required(login_url="/users/signin/")
def post_request_handling(request, form):
    form.save()
    return redirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/users/signin/")
def delete_user(request, id):
    user = User.objects.get(id=id)
    user.delete()
    return redirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/users/signin/")
def update_user(request, id):
    user = User.objects.get(id=id)
    if request.method == "POST":
        user.username = request.POST.get("username")
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        user.save()
    return redirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/users/signin/")
def user_change_password(request, id):
    user = User.objects.get(id=id)
    if request.method == "POST":
        user.set_password(request.POST.get("password"))
        user.save()
    return redirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/users/signin/")
def upload_document(request):
    Document = apps.get_model(
        "users", "Document"
    )  # Dynamically load the Document model

    if request.method == "POST":
        title = request.POST.get("title")
        doc_type = request.POST.get("doc_type")
        file = request.FILES.get("file")

        if title and doc_type and file:  # Ensure a file is provided
            Document.objects.create(
                title=title, doc_type=doc_type, file=file, user=request.user
            )
            messages.success(request, "Document uploaded successfully.")
        else:
            messages.error(request, "All fields, including the file, are required.")

    return redirect("profile")  # Redirect back to the profile page


@login_required(login_url="/users/signin/")
def delete_document(request, doc_id):
    document = get_object_or_404(Document, id=doc_id, user=request.user)
    if request.method == "POST":
        document.delete()
        messages.success(request, "Document removed successfully.")
    return redirect("profile")
