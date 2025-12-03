from rest_framework import serializers

from ..models import Offer, OfferDetail

class OfferDetailSerializer(serializers.ModelSerializer):
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
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    details = OfferDetailSerializer(many=True)
 
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
        ]
        read_only_fields = ['user', 'id', 'created_at', 'updated_at', 'min_price', 'min_delivery_time']

    def validate_details(self, value):
        if len(value) != 3:
            raise serializers.ValidationError({"errors": "An offer must have 3 details."})
        types = [d.get('offer_type') for d in value]
        if len(set(types)) != 3:
            raise serializers.ValidationError({"errosrs": "An offer must have one detail of each type: basic, standard, premium."})
        return value
    
    def create(self, validated_data):
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)

        for detail in details_data:
            OfferDetail.objects.create(offer=offer, **detail)

        return offer
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        if request and request.method == 'GET':
            data['details'] = [
                {
                    'id': d.id,
                    'url': f"/offerdetails/{d.id}/",
                }
                for d in instance.details.all()
            ]
        return data
    
