from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    joined_event_code = models.CharField(max_length=50, null=True, blank=True, help_text="Event that the user joined")

    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class Event(models.Model):
    name = models.CharField(max_length=255, help_text="Name of the event")
    description = models.TextField(blank=True, help_text="Description of the event (Optional)")
    event_code = models.CharField(max_length=50, unique=True, help_text="Unique code for students to access the event")
    start_time = models.DateTimeField(help_text="When the event starts")
    end_time = models.DateTimeField(help_text="When the event ends")
    is_active = models.BooleanField(default=True, help_text="Only one event can be active at a time")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-start_time']

class Photo(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='photos', help_text="Event that the photo belongs to")
    image = models.ImageField(upload_to='event_photos/', help_text="Photo of the event")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, help_text="User who uploaded the photo")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True, help_text="Description of the photo (Optional)")

    def __str__(self):
        return f"Photo from {self.event.name} by {self.uploaded_by.email if self.uploaded_by else 'Anonymous'} at {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['-uploaded_at']

