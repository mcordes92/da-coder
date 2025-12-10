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
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = None

    """
        Permission

        - GET: IsAuthenticated
        - POST: IsAuthenticated and type = customer
        - PATCH: IsAuthenticated and type = business
        - DELETE: IsStaffUser
    """

    def get_permissions(self):
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
        action = self.action

        if action == 'list':
            return Orders.objects.filter(
                Q(customer_user=self.request.user) | Q(business_user=self.request.user)
            )
        else:
            return Orders.objects.all()

class CountInProgressOrdersView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)

        if user.profile.type != 'business':
            return Response({'detail': 'User is not a business user.'}, status=status.HTTP_404_NOT_FOUND)

        count = Orders.objects.filter(
            business_user=user,
            status='in_progress'
        ).count()

        return Response({'order_count': count}, status=status.HTTP_200_OK)
    

class CountCompletedOrdersView(views.APIView):
    passpermission_classes = [IsAuthenticated]
    
    def get(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)

        if user.profile.type != 'business':
            return Response({'detail': 'User is not a business user.'}, status=status.HTTP_404_NOT_FOUND)

        count = Orders.objects.filter(
            business_user=user,
            status='completed'
        ).count()

        return Response({'completed_order_count': count}, status=status.HTTP_200_OK)