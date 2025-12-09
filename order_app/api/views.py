from django.contrib.auth.models import User
from django.db.models import Min, Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, views, status, filters as drf_filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import OrderSerializer
from ..models import Orders

class OrdersViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = None


    def get_queryset(self):
        action = self.action

        if action == 'list':
            return Orders.objects.filter(
                Q(customer_user=self.request.user) | Q(business_user=self.request.user)
            )
        else:
            return Orders.objects.all()
        
