from django.contrib.auth.models import User
from django.db import models
from django.db.models import Min

class Offer(models.Model):
    """Model representing a service offer created by business users."""
    user = models.ForeignKey(User, related_name='offers', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    image = models.FileField(upload_to='static/offers/', null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def min_price(self):
        """Return the minimum price among all offer details."""
        return self.details.aggregate(min_value=Min('price'))['min_value']
    
    def min_delivery_time(self):
        """Return the minimum delivery time among all offer details."""
        return self.details.aggregate(min_value=Min('delivery_time_in_days'))['min_value']
    
    def __str__(self):
        return self.title
    
class OfferDetail(models.Model):
    """Model representing detailed pricing tiers for an offer (basic, standard, premium)."""
    OFFER_TYPE_CHOICES = [
        ('basic', 'basic'),
        ('standard', 'standard'),
        ('premium', 'premium'),
    ]

    offer = models.ForeignKey(Offer, related_name='details', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.PositiveIntegerField()
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)

    def __str__(self):
        return f"{self.offer.title} - {self.offer_type}"