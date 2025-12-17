from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    """Extended user profile with additional information for customers and businesses."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    file = models.FileField(upload_to='static/profiles/', null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    tel = models.CharField(max_length=15, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    working_hours = models.CharField(max_length=100, null=True, blank=True)

    type = models.CharField(max_length=20, choices=[('customer', 'customer'), ('business', 'business')])

    created_at = models.DateTimeField(auto_now_add=True)