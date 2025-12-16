from django_filters import rest_framework as filters

from ..models import Reviews

class ReviewFilter(filters.FilterSet):
    business_user_id = filters.NumberFilter(field_name='business_user__id')
    reviewer_id = filters.NumberFilter(field_name='reviewer__id')

    class Meta:
        model = Reviews
        fields = ['business_user_id', 'reviewer_id']