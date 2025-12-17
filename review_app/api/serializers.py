from django.contrib.auth.models import User

from rest_framework import serializers

from ..models import Reviews

class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for reviews with business user filtering."""
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)
    business_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(profile__type='business'))

    class Meta:
        model = Reviews
        fields = [
            'id',
            'business_user',
            'reviewer',
            'rating',
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'reviewer']

    def validate(self, attrs):
        """Validate review data and restrict field updates."""
        request = self.context.get('request')
        view = self.context.get('view')
        action = getattr(view, 'action', None) if view else None

        if request and request.method in ['PATCH', 'PUT'] and action in ['partial_update', 'update']:
            allowed = {'rating', 'description'}
            sent = set(getattr(self, 'initial_data', {}).keys())
            disallowed = sent - allowed

            if disallowed:
                raise serializers.ValidationError({k: 'This field cannot be updated.' for k in disallowed})
        
        return attrs
