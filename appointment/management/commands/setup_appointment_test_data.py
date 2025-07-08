# management/commands/setup_appointment_test_data.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from appointment.models import Service, StaffMember, WorkingHours
from datetime import time, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Sets up test data for the appointment system'

    def handle(self, *args, **options):
        # Create a test service
        service, created = Service.objects.get_or_create(
            name='General Consultation',
            defaults={
                'description': 'General medical consultation',
                'duration': timedelta(minutes=30),  # 30 minutes
                'price': 100.00,
                'currency': 'USD',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created service: {service.name}'))
        else:
            self.stdout.write(f'Service already exists: {service.name}')

        # Create a test doctor/staff member if one doesn't exist
        try:
            # Try to find an existing user to make a staff member
            user = User.objects.filter(is_staff=True).first()
            if not user:
                # Create a test user
                user = User.objects.create_user(
                    username='test_doctor',
                    email='doctor@example.com',
                    password='testpass123',
                    first_name='Dr. John',
                    last_name='Smith',
                    is_staff=True
                )
                self.stdout.write(self.style.SUCCESS(f'Created test user: {user.username}'))
            
            # Create staff member
            staff_member, created = StaffMember.objects.get_or_create(
                user=user,
                defaults={
                    'slot_duration': 30,
                    'lead_time': 24,  # 24 hours
                    'finish_time': 2,  # 2 hours before end of day
                    'appointment_buffer_time': 0,
                }
            )
            
            if created:
                # Add the service to the staff member
                staff_member.services_offered.add(service)
                self.stdout.write(self.style.SUCCESS(f'Created staff member: {staff_member.get_staff_member_name()}'))
                
                # Create working hours for Monday-Friday 9 AM to 5 PM
                working_days = [
                    ('Monday', 1),
                    ('Tuesday', 2), 
                    ('Wednesday', 3),
                    ('Thursday', 4),
                    ('Friday', 5)
                ]
                
                for day_name, day_num in working_days:
                    working_hours, wh_created = WorkingHours.objects.get_or_create(
                        staff_member=staff_member,
                        day_of_week=day_num,
                        defaults={
                            'start_time': time(9, 0),  # 9:00 AM
                            'end_time': time(17, 0),   # 5:00 PM
                        }
                    )
                    if wh_created:
                        self.stdout.write(f'Created working hours for {day_name}: 9:00 AM - 5:00 PM')
            else:
                # Make sure the service is added to existing staff member
                staff_member.services_offered.add(service)
                self.stdout.write(f'Staff member already exists: {staff_member.get_staff_member_name()}')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating staff member: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Test data setup completed!'))
