from django.db import models
from django.contrib.auth.models import User
from shortuuid.django_fields import ShortUUIDField
from shortuuid import uuid



ROLE_CHOICES = (
    ("admin", "Admin"),
    ("user", "User"),
)


class Profile(models.Model):
    uuid = ShortUUIDField(default=uuid, editable=False, unique=True)  # Add default value
    USER_TYPE_CHOICES = (
        ("doctor", "Doctor"),
        ("patient", "Patient"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    user_type = models.CharField(
        max_length=10, choices=USER_TYPE_CHOICES, default="patient"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")
    full_name = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)  # Fixed max_length
    zip_code = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.ImageField(upload_to="avatar", null=True, blank=True)
    pre_existing_conditions = models.TextField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, null=True, blank=True
    )
    BUDGET_CHOICES = [
        ("low", "Low"),
        ("mid_low", "Mid Low"),
        ("medium", "Medium"),
        ("mid_high", "Mid High"),
        ("high", "High"),
    ]
    budget = models.CharField(
        max_length=20, choices=BUDGET_CHOICES, null=True, blank=True
    )

    def __str__(self):
        return self.user.username


class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    doc_type = models.CharField(max_length=50)
    file = models.FileField(upload_to="documents/")
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title