from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from appointment.models import Service, StaffMember
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up sample appointment services and staff for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up sample appointment data...'))

        # Create services
        services_data = [
            {
                'name': 'General Consultation',
                'description': 'General medical consultation with our experienced doctors',
                'duration': timedelta(minutes=30),
                'price': 150.00,
                'currency': 'USD',
                'allow_rescheduling': True,
                'reschedule_limit': 2,
            },
            {
                'name': 'Health Checkup',
                'description': 'Comprehensive health checkup including basic tests',
                'duration': timedelta(hours=1),
                'price': 300.00,
                'currency': 'USD',
                'allow_rescheduling': True,
                'reschedule_limit': 1,
            },
            {
                'name': 'Specialist Consultation',
                'description': 'Consultation with specialist doctors',
                'duration': timedelta(minutes=45),
                'price': 250.00,
                'currency': 'USD',
                'allow_rescheduling': True,
                'reschedule_limit': 1,
            },
            {
                'name': 'Follow-up Visit',
                'description': 'Follow-up visit for ongoing treatment',
                'duration': timedelta(minutes=15),
                'price': 75.00,
                'currency': 'USD',
                'allow_rescheduling': True,
                'reschedule_limit': 3,
            },
        ]

        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )
            if created:
                self.stdout.write(f'Created service: {service.name}')
            else:
                self.stdout.write(f'Service already exists: {service.name}')

        # Create staff members from existing doctors
        doctors = User.objects.filter(groups__name='Doctor')
        
        if not doctors.exists():
            self.stdout.write(self.style.WARNING('No doctors found in the system. Please create some doctor accounts first.'))
            return

        for doctor in doctors:
            staff_member, created = StaffMember.objects.get_or_create(
                user=doctor,
                defaults={
                    'slot_duration': 30,
                    'work_on_saturday': True,
                    'work_on_sunday': False,
                }
            )
            
            if created:
                # Add all services to this staff member
                services = Service.objects.all()
                staff_member.services_offered.set(services)
                self.stdout.write(f'Created staff member: {staff_member.get_staff_member_name()}')
            else:
                self.stdout.write(f'Staff member already exists: {staff_member.get_staff_member_name()}')

        self.stdout.write(self.style.SUCCESS('Sample appointment data setup completed!'))
        self.stdout.write(f'Created {Service.objects.count()} services')
        self.stdout.write(f'Created {StaffMember.objects.count()} staff members')
