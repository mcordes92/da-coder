from django.contrib.auth.models import User

from rest_framework.permissions import BasePermission
   
class IsBusinessUser(BasePermission):
    """
    Custom permission to only allow business users to create offers.
    Assumes the user model has a `type` attribute.
    """

    def has_permission(self, request, view):
        """Check if the user is authenticated and is of type 'business'."""
        user = User.objects.get(pk=request.user.pk)

        return request.user.is_authenticated and getattr(user.profile, 'type', None) == 'business'
    
    def has_object_permission(self, request, view, obj):
        """Check if the user is the business user associated with the order."""
        return obj.business_user == request.user
    
class IsCustomerUser(BasePermission):
    """
    Custom permission to only allow business users to create offers.
    Assumes the user model has a `type` attribute.
    """

    def has_permission(self, request, view):
        """Check if the user is authenticated and is of type 'customer'."""
        user = User.objects.get(pk=request.user.pk)

        return request.user.is_authenticated and getattr(user.profile, 'type', None) == 'customer'