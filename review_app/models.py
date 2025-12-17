from django.contrib.auth.models import User
from django.db import models

class Reviews(models.Model):
    """Model representing a review written by a customer for a business user."""
    reviewer = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    business_user = models.ForeignKey(User, related_name='received_reviews', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    