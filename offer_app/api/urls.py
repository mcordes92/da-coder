from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import OffersViewSet

router = DefaultRouter()
router.register(r'offers', OffersViewSet, basename='offers')

urlpatterns = [
    path('', include(router.urls)),
]
