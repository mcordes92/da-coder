from django.contrib.auth.models import User
from django.db.models import Min, Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, views, status, filters as drf_filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend


from .serializers import OfferSerializer, OfferDetailSerializer
from ..models import Offer, OfferDetail
from ..filters.offer_filters import OfferFilter
from .permissions import IsOfferOwner, IsBusinessUser

class OfferPagination(PageNumberPagination):
    """Pagination configuration for offers."""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class OffersViewSet(viewsets.ModelViewSet):
    """ViewSet for managing offers with filtering, searching, and ordering."""
    serializer_class = OfferSerializer
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    pagination_class = OfferPagination


    def get_queryset(self):
        """Return optimized queryset with related user and details."""
        return (
             Offer.objects.all()
        .select_related('user')
        .prefetch_related('details')
        .order_by('-updated_at')
        )
    
    def get_permissions(self):
        """Determine permissions based on action.

        - GET: AllowAny
        - POST: IsAuthenticated and type = business
        - RETRIEVE: IsAuthenticated
        - PATCH, DELETE: IsAuthenticated and owner of the offer
        """
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, IsBusinessUser]
        elif self.action == 'retrieve':
            self.permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsOfferOwner]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Save offer with the current user as owner."""
        serializer.save(user=self.request.user)

class OfferDetailsView(views.APIView):
    """API view for retrieving specific offer detail."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """Retrieve a specific offer detail by ID."""
        offer_detail = get_object_or_404(OfferDetail, pk=pk)
        serializer = OfferDetailSerializer(offer_detail)
        return Response(serializer.data, status=status.HTTP_200_OK)