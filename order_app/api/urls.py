from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import OrdersViewSet

router = DefaultRouter()
router.register(r'orders', OrdersViewSet, basename='orders')

urlpatterns = [
    #path('offerdetails/<int:pk>/', OfferDetailsView.as_view(), name='offer-details'),
    path('', include(router.urls)),
]
