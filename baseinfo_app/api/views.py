from django.db import models

from rest_framework import generics, mixins, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from review_app.models import Reviews
from offer_app.models import Offer
from profile_app.models import Profile

class BaseInfoView(mixins.ListModelMixin, generics.GenericAPIView):
    """API view for retrieving base platform statistics."""
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """Return platform statistics including reviews, ratings, businesses, and offers."""
        review_count = Reviews.objects.all().count()
        average_rating = Reviews.objects.aggregate(avg_rating=models.Avg('rating'))['avg_rating'] or 0
        business_profile_count = Profile.objects.filter(type='business').count()
        offer_count = Offer.objects.all().count()


        data = {
            'review_count': review_count,
            'average_rating': average_rating,
            'business_profile_count': business_profile_count,
            'offer_count': offer_count,
        }
        return Response(data, status=status.HTTP_200_OK)