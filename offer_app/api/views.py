from django.contrib.auth.models import User
from django.db.models import Min, Q
from rest_framework import viewsets, views, status, filters as drf_filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend


from .serializers import OfferSerializer
from ..models import Offer, OfferDetail
from ..filters.offer_filters import OfferFilter

class OfferPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 100

class OffersViewSet(viewsets.ModelViewSet):
    serializer_class = OfferSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    pagination_class = OfferPagination


    def get_queryset(self):
        return (
             Offer.objects.all()
        .select_related('user')
        .prefetch_related('details')
        )

    # TODO: get_permissions einbauen, GET, PATCH, DELETE für PK

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)