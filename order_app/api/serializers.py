from rest_framework import serializers

from ..models import Orders
from offer_app.models import OfferDetail

class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders with offer detail information."""
    offer_detail_id = serializers.PrimaryKeyRelatedField(queryset=OfferDetail.objects.all(), source='offer_detail', read_only=False, error_messages={'does_not_exist': 'Offer detail with the given ID does not exist.'})
 
    title = serializers.CharField(source='offer_detail.title', read_only=True)
    revisions = serializers.IntegerField(source='offer_detail.revisions', read_only=True)
    delivery_time_in_days = serializers.IntegerField(source='offer_detail.delivery_time_in_days', read_only=True)
    price = serializers.IntegerField(source='offer_detail.price', read_only=True)
    features = serializers.JSONField(source='offer_detail.features', read_only=True)
    offer_type = serializers.CharField(source='offer_detail.offer.offer_type', read_only=True)

    status = serializers.CharField(required=False)

    class Meta:
        model = Orders
        fields = [
            'offer_detail_id',
            'id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status',
            'created_at',
            'updated_at'         
        ]
        read_only_fields = ['id', 'customer_user', 'business_user', 'created_at', 'updated_at', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']


    def validate(self, attrs):
        """Validate order data based on the request method and action."""
        attrs = super().validate(attrs)

        request = self.context.get('request')
        view = self.context.get('view')
        method = getattr(request, 'method', None)
        action = getattr(view, 'action', None)
        initial = self.initial_data or {}

        if method == 'POST' and action == 'create':
            allowed = required = {'offer_detail_id'}
        elif method == 'PATCH' and action == 'partial_update':
            allowed = required = {'status'}
        else:
            return attrs
        
        sent = set(initial)
        errors = {}

        for f in sent - allowed:
            errors.setdefault(f, []).append('This field is not allowed.')

        for f in required - sent:
            errors.setdefault(f, []).append('This field is required.')

        status_value = initial.get('status')

        if status_value is not None:
            valid_statuses = [c[0] for c in Orders.status_choices]

            if status_value not in valid_statuses:
                errors.setdefault('status', []).append(f'Status must be one of: {", ".join(valid_statuses)}.')

        if errors:
            raise serializers.ValidationError(errors)
        
        return attrs

    def create(self, validated_data):
        """Create a new order with customer and business user assignment."""
        request = self.context.get('request')

        offer_detail = validated_data['offer_detail']

        validated_data['business_user'] = offer_detail.offer.user
        validated_data['customer_user'] = request.user


        offer = Orders.objects.create(**validated_data)

        return offer
    
    def to_representation(self, instance):
        """Customize representation based on request method and action."""
        data = super().to_representation(instance)
        request = self.context.get('request')
        view = self.context.get('view')   

        action = getattr(view, 'action', None) if view else None

        data.pop("offer_detail_id", None)
       
        if request and request.method == 'POST' and action == 'create':
            data.pop("updated_at", None)
            
            return data

        return data

    
