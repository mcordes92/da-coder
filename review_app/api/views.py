from django.contrib.auth.models import User
from django.db.models import Min, Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, views, status, filters as drf_filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import ReviewSerializer
from ..filters.review_filters import ReviewFilter
from ..models import Reviews
from .permissions import IsCustomerUser, IsReviewer


class ReviewsViewSet(viewsets.ModelViewSet):
    """ViewSet for managing reviews with filtering and ordering."""
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['updated_at', 'rating']
    queryset = None

    def get_queryset(self):
        """Return all reviews ordered by update time."""
        return (
             Reviews.objects.all()
        .order_by('-updated_at')
        )

    def get_permissions(self):
        """Determine permissions based on action.

        - GET: IsAuthenticated
        - POST: IsAuthenticated and type = customer and profile exists
        - PATCH: IsAuthenticated and reviewer is the author
        - DELETE: IsAuthenticated and reviewer is the author
        """
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, IsCustomerUser]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsReviewer]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """Save review with the current user as reviewer."""
        serializer.save(reviewer=self.request.user)
