from django.contrib.auth.models import User
from django.db.models import Min, Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, views, status, filters as drf_filters
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import OrderSerializer
from ..models import Orders
from .permissions import IsBusinessUser, IsCustomerUser

class OrdersViewSet(viewsets.ModelViewSet):
    """ViewSet for managing orders with role-based permissions."""
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = None

    def get_permissions(self):
        """Determine permissions based on action.

        - GET: IsAuthenticated
        - POST: IsAuthenticated and type = customer
        - PATCH: IsAuthenticated and type = business
        - DELETE: IsStaffUser
        """
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, IsCustomerUser]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsBusinessUser]
        elif self.action == 'destroy':
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        """Return orders filtered by user involvement (customer or business)."""
        action = self.action

        if action == 'list':
            return Orders.objects.filter(
                Q(customer_user=self.request.user) | Q(business_user=self.request.user)
            )
        else:
            return Orders.objects.all()

class CountInProgressOrdersView(views.APIView):
    """API view for counting in-progress orders for a business user."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk, format=None):
        """Return count of in-progress orders for the specified business user."""
        user = get_object_or_404(User, pk=pk)

        if user.profile.type != 'business':
            return Response({'detail': 'User is not a business user.'}, status=status.HTTP_404_NOT_FOUND)

        count = Orders.objects.filter(
            business_user=user,
            status='in_progress'
        ).count()

        return Response({'order_count': count}, status=status.HTTP_200_OK)
    

class CountCompletedOrdersView(views.APIView):
    """API view for counting completed orders for a business user."""
    passpermission_classes = [IsAuthenticated]
    
    def get(self, request, pk, format=None):
        """Return count of completed orders for the specified business user."""
        user = get_object_or_404(User, pk=pk)

        if user.profile.type != 'business':
            return Response({'detail': 'User is not a business user.'}, status=status.HTTP_404_NOT_FOUND)

        count = Orders.objects.filter(
            business_user=user,
            status='completed'
        ).count()

        return Response({'completed_order_count': count}, status=status.HTTP_200_OK)