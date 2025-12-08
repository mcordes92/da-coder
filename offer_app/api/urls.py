from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import OffersViewSet, OfferDetailsView

router = DefaultRouter()
router.register(r'offers', OffersViewSet, basename='offers')

urlpatterns = [
    path('offerdetails/<int:pk>/', OfferDetailsView.as_view(), name='offer-details'),
    path('', include(router.urls)),
]
