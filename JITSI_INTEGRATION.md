# Jitsi Meet Integration - MyDoctor

## Overview
This implementation integrates Jitsi Meet video conferencing into the MyDoctor appointment system, allowing patients and doctors to have video consultations directly through the web application.

## Features

### 1. **Automatic Meeting Room Creation**
- Each appointment automatically gets a unique meeting room ID
- Room IDs are generated using the format: `consultation-{unique_id}`
- Rooms are persistent and can be accessed by both doctor and patient

### 2. **Role-Based Access**
- **Patients**: Can join consultations for appointments they have booked
- **Doctors**: Can join consultations for appointments assigned to them
- **Security**: Only authorized users can access specific consultation rooms

### 3. **Appointment Status Management**
- **Pending**: Appointments start as pending and need doctor confirmation
- **Confirmed**: Only confirmed appointments allow video consultations
- **Canceled**: Canceled appointments cannot be joined

### 4. **Time-Based Access Control**
- Consultations can be joined 30 minutes before the appointment
- Access is available up to 2 hours after the appointment time
- Prevents unauthorized access outside appointment windows

## User Interface

### Patient View
- **Appointment List**: Shows all appointments with status indicators
- **Join Consultation**: Blue button appears for confirmed appointments
- **Status Badges**: Color-coded status indicators (green=confirmed, yellow=pending, red=canceled)

### Doctor View
- **Appointment Management**: Shows all patient appointments
- **Confirm Appointments**: Green button to confirm pending appointments
- **Join Consultation**: Access to video consultation rooms
- **Patient Information**: Full patient details visible

### Consultation Room
- **Full-Screen Video**: Jitsi Meet embedded interface
- **Meeting Controls**: Video/audio toggle, screen share, chat, etc.
- **Appointment Details**: Context panel showing appointment information
- **Easy Navigation**: Back to appointments with one click

## Technical Implementation

### Models
```python
# Added to Appointment model
meeting_room_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
```

### Views
- `join_consultation()`: Handles video consultation access
- `confirm_appointment()`: Allows doctors to confirm appointments

### Templates
- `consultation_room.html`: Full Jitsi Meet interface
- Updated `appointment_list.html`: Patient consultation access
- Updated `doctor_appointments.html`: Doctor consultation access

### URLs
- `/appointments/consultation/<id>/`: Join consultation room
- `/appointments/confirm/<id>/`: Confirm appointment (doctors only)

## Setup Instructions

### 1. **Database Migration**
```bash
python manage.py makemigrations appointments
python manage.py migrate appointments
```

### 2. **Create Test Data** (Optional)
```bash
python manage.py create_test_appointments
```

### 3. **User Groups**
Ensure users are assigned to appropriate groups:
- **Doctor**: Can confirm appointments and join consultations
- **Patient**: Can book appointments and join consultations

### 4. **Email Configuration**
Configure email settings in `settings.py` for appointment notifications:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-smtp-server.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@domain.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

## Security Features

### 1. **Authentication Required**
- All consultation access requires user authentication
- Users must be logged in to join consultations

### 2. **Authorization Checks**
- Only appointment participants can access consultation rooms
- Doctors can only confirm their own appointments
- Patients can only access their own appointments

### 3. **Time-Based Access**
- Consultations have time-based access windows
- Prevents access to old or future appointments beyond reasonable limits

### 4. **Status Validation**
- Only confirmed appointments allow video consultations
- Pending appointments must be confirmed by doctors first

## Testing

### 1. **Create Test Users**
```bash
python manage.py create_test_appointments
```

### 2. **Test Workflow**
1. Login as doctor (testdoctor / testpass123)
2. Confirm pending appointments
3. Login as patient (testpatient / testpass123)
4. Join confirmed consultations
5. Test video conferencing features

### 3. **Manual Testing**
- Test time-based access restrictions
- Test unauthorized access attempts
- Test video/audio functionality
- Test different browsers and devices

## Customization Options

### 1. **Jitsi Meet Server**
Change the Jitsi Meet server by modifying the `domain` in `consultation_room.html`:
```javascript
const domain = 'your-jitsi-server.com';
```

### 2. **Meeting Room Naming**
Customize room ID format in `models.py`:
```python
def generate_meeting_room_id(self):
    return f"your-prefix-{uuid.uuid4().hex[:12]}"
```

### 3. **Access Time Windows**
Modify time restrictions in `views.py`:
```python
# Allow joining 1 hour before and 3 hours after
time_window_before = 1 * 60 * 60  # 1 hour
time_window_after = 3 * 60 * 60   # 3 hours
```

### 4. **Interface Configuration**
Customize Jitsi Meet interface in `consultation_room.html`:
```javascript
interfaceConfigOverwrite: {
    TOOLBAR_BUTTONS: [...], // Customize toolbar
    SHOW_JITSI_WATERMARK: false, // Hide watermark
    // Add more customizations
}
```

## Troubleshooting

### Common Issues

1. **Video Not Loading**
   - Check internet connection
   - Verify Jitsi Meet server accessibility
   - Check browser permissions for camera/microphone

2. **Unable to Join Consultation**
   - Verify appointment is confirmed
   - Check if within time window
   - Confirm user has proper permissions

3. **Meeting Room Not Found**
   - Verify meeting_room_id exists in database
   - Check for database migration issues
   - Ensure room ID generation is working

### Debug Steps

1. Check Django logs for errors
2. Verify database migrations are applied
3. Test with different users and appointment statuses
4. Check browser console for JavaScript errors
5. Verify Jitsi Meet external API is loading

## Future Enhancements

1. **Recording Capabilities**: Add consultation recording
2. **Appointment Notes**: Post-consultation notes and summaries
3. **Mobile App Integration**: React Native or Flutter app
4. **Custom Jitsi Server**: Self-hosted Jitsi Meet instance
5. **Advanced Scheduling**: Recurring appointments and availability
6. **Analytics**: Consultation duration and quality metrics

## Support

For issues or questions:
1. Check Django logs for error messages
2. Verify all migrations are applied
3. Test with different browsers
4. Check Jitsi Meet documentation for API issues
