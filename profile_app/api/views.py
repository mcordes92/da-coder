from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework import generics, mixins, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import ProfileSerializer, BusinessProfileSerializer, CustomerProfileSerializer, BaseProfileSerializer
from ..models import Profile
from .permissions import IsProfileOwnerOrReadOnly

from ..models import Profile as Profiles

class ProfileView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):

    permission_classes = [IsProfileOwnerOrReadOnly]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    lookup_field = 'pk'

    def get_object(self):
        return get_object_or_404(Profile, user=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    
class ProfilesListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.all()
    mode = None

    def get_dispatch(self, request, *args, **kwargs):
        if 'mode' in kwargs:
            self.mode = kwargs.pop('mode')
        return super().get_dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        query_set = Profiles.objects.all()

        if self.mode == 'business':
            query_set = query_set.filter(type='business')
        elif self.mode == 'customer':
            query_set = query_set.filter(type='customer')
        return query_set
    
    def get_serializer_class(self):
        if self.mode == 'business':
            return BusinessProfileSerializer
        elif self.mode == 'customer':
            return CustomerProfileSerializer
        return BaseProfileSerializer