from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import OrdersViewSet, CountInProgressOrdersView, CountCompletedOrdersView

router = DefaultRouter()
router.register(r'orders', OrdersViewSet, basename='orders')

urlpatterns = [
    path('order-count/<int:pk>/', CountInProgressOrdersView.as_view(), name='order-count-in-progress'),
    path('completed-order-count/<int:pk>/', CountCompletedOrdersView.as_view(), name='order-count-completed'),
    path('', include(router.urls)),
]
