from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
        ('relative', 'Relative'),
    )
    
    # New IoT Platform Choices
    IOT_CHOICES = (
        ('none', 'None / Will add later'),
        ('thingspeak', 'ThingSpeak'),
        ('blynk', 'Blynk IoT'),
    )

    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='patient')
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    # The new Dropdown to select the platform
    iot_platform = models.CharField(max_length=20, choices=IOT_CHOICES, default='none')
    
    # ThingSpeak Fields (Existing)
    thingspeak_channel_id = models.CharField(max_length=50, blank=True, null=True)
    thingspeak_read_key = models.CharField(max_length=50, blank=True, null=True)
    
    # Blynk Field (New)
    blynk_auth_token = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class AccessControl(models.Model): 
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='granted_access')
    granted_to = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='accessed_patients')
    
    class Meta:
        unique_together = ('patient', 'granted_to')

    def __str__(self):
        return f"{self.granted_to.username} can access {self.patient.username}"