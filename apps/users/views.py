from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from django.views.generic import CreateView
from apps.common.models import Product
from apps.users.models import Profile, Document  # Move the import to the top
from apps.users.forms import SigninForm, SignupForm, UserPasswordChangeForm, UserSetPasswordForm, UserPasswordResetForm, ProfileForm
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

@login_required(login_url='/users/signin/')
def index(request):

    prodName = ''
    
    if len( Product.objects.all() ):
        prodName = Product.objects.all()[0].name
        
    return HttpResponse("INDEX Users" + ' ' + prodName)


class SignInView(LoginView):
    form_class = SigninForm
    template_name = "authentication/sign-in.html"

class SignUpView(CreateView):
    form_class = SignupForm
    template_name = "authentication/sign-up.html"
    success_url = "/users/signin/"  # Redirect after successful signup

    def form_valid(self, form):
        user = form.save()  # Save the new user
        login(self.request, user)  # Log in the user immediately
        return super().form_valid(form)

    def form_invalid(self, form):
        # Print errors in the console for debugging
        print(form.errors)
        return super().form_invalid(form)

class UserPasswordChangeView(PasswordChangeView):
    template_name = 'authentication/password-change.html'
    form_class = UserPasswordChangeForm

class UserPasswordResetView(PasswordResetView):
    template_name = 'authentication/forgot-password.html'
    form_class = UserPasswordResetForm
    success_url = '/users/password-reset-done/'  # Add success URL

class UserPasswrodResetConfirmView(PasswordResetConfirmView):
    template_name = 'authentication/reset-password.html'
    form_class = UserSetPasswordForm
    success_url = '/users/password-reset-complete/'  # Add success URL


def signout_view(request):
    logout(request)
    return redirect(reverse('signin'))


@login_required(login_url='/users/signin/')
def profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    documents = Document.objects.filter(user=request.user).order_by('-upload_date')  # Query documents for the logged-in user

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)

        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
    else:
        form = ProfileForm(instance=profile)
    
    context = {
        'form': form,
        'segment': 'profile',
        'documents': documents,  # Pass documents to the template
    }
    return render(request, 'dashboard/profile.html', context)


@login_required(login_url='/users/signin/')
def upload_avatar(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        profile.avatar = request.FILES.get('avatar')
        profile.save()
        messages.success(request, 'Avatar uploaded successfully')
    return redirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='/users/signin/')
def change_password(request):
    user = request.user
    if request.method == 'POST':
        if check_password(request.POST.get('current_password'), user.password):
            user.set_password(request.POST.get('new_password'))
            user.save()
            messages.success(request, 'Password changed successfully')
        else:
            messages.error(request, "Password doesn't match!")
    return redirect(request.META.get('HTTP_REFERER'))



def user_list(request):
    filters = user_filter(request)
    user_list = User.objects.filter(**filters)
    form = SignupForm()

    page = request.GET.get('page', 1)
    paginator = Paginator(user_list, 5)
    users = paginator.page(page)

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            return post_request_handling(request, form)

    context = {
        'users': users,
        'form': form,
    }
    return render(request, 'apps/users.html', context)


@login_required(login_url='/users/signin/')
def post_request_handling(request, form):
    form.save()
    return redirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='/users/signin/')
def delete_user(request, id):
    user = User.objects.get(id=id)
    user.delete()
    return redirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='/users/signin/')
def update_user(request, id):
    user = User.objects.get(id=id)
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
    return redirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='/users/signin/')
def user_change_password(request, id):
    user = User.objects.get(id=id)
    if request.method == 'POST':
        user.set_password(request.POST.get('password'))
        user.save()
    return redirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='/users/signin/')
def upload_document(request):
    Document = apps.get_model('users', 'Document')  # Dynamically load the Document model

    if request.method == 'POST':
        title = request.POST.get('title')
        doc_type = request.POST.get('doc_type')
        file = request.FILES.get('file')

        if title and doc_type and file:  # Ensure a file is provided
            Document.objects.create(title=title, doc_type=doc_type, file=file, user=request.user)
            messages.success(request, 'Document uploaded successfully.')
        else:
            messages.error(request, 'All fields, including the file, are required.')

    return redirect('profile')  # Redirect back to the profile page

@login_required(login_url='/users/signin/')
def delete_document(request, doc_id):
    document = get_object_or_404(Document, id=doc_id, user=request.user)
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Document removed successfully.')
    return redirect('profile')