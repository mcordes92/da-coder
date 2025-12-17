from django.shortcuts import get_object_or_404

from rest_framework import generics, mixins
from rest_framework.permissions import IsAuthenticated

from .serializers import ProfileSerializer, BusinessProfileSerializer, CustomerProfileSerializer, BaseProfileSerializer
from ..models import Profile
from .permissions import IsProfileOwnerOrReadOnly
from ..models import Profile as Profiles

class ProfileView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    """API view for retrieving and updating user profiles."""

    permission_classes = [IsProfileOwnerOrReadOnly]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    lookup_field = 'pk'

    def get_object(self):
        """Retrieve profile by user ID and check permissions."""
        obj = get_object_or_404(Profile, user=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, *args, **kwargs):
        """Handle GET request to retrieve a profile."""
        return self.retrieve(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        """Handle PATCH request to update a profile."""
        return self.partial_update(request, *args, **kwargs)
    
class ProfilesListView(generics.ListAPIView):
    """API view for listing profiles filtered by type (business or customer)."""
    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.all()
    mode = None

    def get_dispatch(self, request, *args, **kwargs):
        """Handle dispatch with mode parameter."""
        if 'mode' in kwargs:
            self.mode = kwargs.pop('mode')
        return super().get_dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        """Return profiles filtered by type based on mode."""
        query_set = Profiles.objects.all()

        if self.mode == 'business':
            query_set = query_set.filter(type='business')
        elif self.mode == 'customer':
            query_set = query_set.filter(type='customer')
        return query_set
    
    def get_serializer_class(self):
        """Return appropriate serializer based on profile type."""
        if self.mode == 'business':
            return BusinessProfileSerializer
        elif self.mode == 'customer':
            return CustomerProfileSerializer
        return BaseProfileSerializer