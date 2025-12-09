from django.db import models
from django.contrib.auth.models import User

from offer_app.models import OfferDetail

class Orders(models.Model):
    offer_detail = models.ForeignKey(OfferDetail, on_delete=models.CASCADE, related_name='orders')

    customer_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_orders')

    status_choices = [
        ('in_progress', 'in_progress'),
        ('completed', 'completed'),
        ('cancelled', 'cancelled'),
    ]

    status = models.CharField(max_length=50, default='in_progress', choices=status_choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
