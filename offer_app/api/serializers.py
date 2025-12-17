from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.reverse import reverse

from ..models import Offer, OfferDetail

class OfferDetailSerializer(serializers.ModelSerializer):
    """Serializer for offer detail pricing tiers."""
    class Meta:
        model = OfferDetail
        fields = [
            'id',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
        ]

class OfferSerializer(serializers.ModelSerializer):
    """Serializer for offers with nested details and user information."""
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    details = OfferDetailSerializer(many=True)

    user_details = serializers.SerializerMethodField(read_only=True)
 
    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
            'details',
            'min_price',
            'min_delivery_time',
            'user_details',
        ]
        read_only_fields = ['user', 'id', 'created_at', 'updated_at', 'min_price', 'min_delivery_time', 'user_details']

    def validate_details(self, value):
        """Validate that an offer has exactly 3 details (basic, standard, premium)."""
        if self.instance is None:
            if len(value) != 3:
                raise serializers.ValidationError({"errors": "An offer must have 3 details."})
            types = [d.get('offer_type') for d in value]
            if len(set(types)) != 3:
                raise serializers.ValidationError({"errosrs": "An offer must have one detail of each type: basic, standard, premium."})
        
        return value
    
    def create(self, validated_data):
        """Create a new offer with associated details."""
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)

        for detail in details_data:
            OfferDetail.objects.create(offer=offer, **detail)

        return offer
    
    def update(self, instance, validated_data):
        """Update an existing offer and its details."""
        details_data = validated_data.pop('details', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:

            for detail_data in details_data:
                offer_type = detail_data.get('offer_type')

                if offer_type is None:
                    raise serializers.ValidationError({"errors": "Each detail must have an offer_type for update."})
                
                try:
                    detail_instance = OfferDetail.objects.get(offer_type=offer_type, offer=instance)
                except OfferDetail.DoesNotExist:
                    raise serializers.ValidationError({"errors": f"OfferDetail with offer_type {offer_type} does not exist for this offer."})
                
                detail_data = detail_data.copy()
                detail_data.pop('id', None)
                detail_data.pop('offer_type', None)

                for attr, value in detail_data.items():
                    setattr(detail_instance, attr, value)
                detail_instance.save()
        
        return instance


    def get_user_details(self, obj):
        """Return basic user details for the offer owner."""
        user = obj.user
        return {
            'first_name': user.profile.first_name,
            'last_name': user.profile.last_name,
            'username': user.username,
        }
    
    def to_representation(self, instance):
        """Customize representation based on request method and action."""
        data = super().to_representation(instance)
        request = self.context.get('request')
        view = self.context.get('view')   

        action = getattr(view, 'action', None) if view else None

        if request and request.method == 'GET' and action == 'list':
            data['details'] = [
                {
                    'id': d.id,
                    'url': f"/offerdetails/{d.id}/",
                }
                for d in instance.details.all()
            ]

            return data
        
        if request and request.method == 'GET' and action == 'retrieve':
            data.pop("user_details", None)
            data['details'] = [
                {
                    'id': d.id,
                    'url': reverse('offers-detail', args=[d.id], request=request),
                }
                for d in instance.details.all()
            ]

            return data
        
        data.pop("user_details", None)
        data.pop("min_price", None)
        data.pop("min_delivery_time", None)

        return data
    
