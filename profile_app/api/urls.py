from django.urls import path
from .views import ProfileView, ProfilesListView

urlpatterns = [
    path('profile/<int:pk>/', ProfileView.as_view(), name='profileGetPatch'),
    path('profiles/business/', ProfilesListView.as_view(mode='business'), name='profilesListBusiness'),
    path('profiles/customer/', ProfilesListView.as_view(mode='customer'), name='profilesListCustomer'),
]
