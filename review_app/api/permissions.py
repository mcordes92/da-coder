from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotFound

from django.contrib.auth.models import User
       
class IsCustomerUser(BasePermission):
    """
    Custom permission to only allow business users to create offers.
    Assumes the user model has a `type` attribute.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated and is of type 'customer'
        user = User.objects.get(pk=request.user.pk)

        return request.user.is_authenticated and getattr(user.profile, 'type', None) == 'customer'
    
class IsReviewer(BasePermission):
    """
    Custom permission to only allow owners of an offer to edit or delete it.
    Assumes the view has a `get_object()` method that returns the offer instance.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the user is the owner of the offer
        return obj.reviewer == request.user