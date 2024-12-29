
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create user groups and assign permissions'

    def handle(self, *args, **kwargs):
        # Create groups
        admin_group, created = Group.objects.get_or_create(name='Admin')
        patient_group, created = Group.objects.get_or_create(name='Patient')
        doctor_group, created = Group.objects.get_or_create(name='Doctor')

        # Assign permissions to groups
        if created:
            self.stdout.write(self.style.SUCCESS(f'Group "{admin_group.name}" created'))
        if created:
            self.stdout.write(self.style.SUCCESS(f'Group "{patient_group.name}" created'))
        if created:
            self.stdout.write(self.style.SUCCESS(f'Group "{doctor_group.name}" created'))

        # Add permissions to groups
        # Admin group gets all permissions
        admin_permissions = Permission.objects.all()
        admin_group.permissions.set(admin_permissions)

        # Patient group gets limited permissions
        patient_permissions = Permission.objects.filter(codename__in=[
            'add_appointment', 'change_appointment', 'delete_appointment', 'view_appointment'
        ])
        patient_group.permissions.set(patient_permissions)

        # Doctor group gets limited permissions
        doctor_permissions = Permission.objects.filter(codename__in=[
            'change_appointment', 'view_appointment'
        ])
        doctor_group.permissions.set(doctor_permissions)

        self.stdout.write(self.style.SUCCESS('Permissions assigned to groups'))

        # Create a superuser and assign to admin group
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')
            admin_user.groups.add(admin_group)
            self.stdout.write(self.style.SUCCESS('Superuser "admin" created and assigned to Admin group'))