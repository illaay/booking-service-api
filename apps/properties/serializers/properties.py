from rest_framework import serializers
from apps.properties.models import Property
from apps.core.models import LodgingType

from ..models import Amenity


class PropertyCreateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    amenities = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Amenity.objects.all(),
        required=False
    )
    lodging_type_choices = serializers.CharField(source='get_lodging_type_display')

    class Meta:
        model = Property
        fields = [
            'owner',
            'country',
            'state',
            'city',
            'street',
            'building',
            'apartment_number',
            'room_number',
            'lodging_type',
            'lodging_type_choices',
            'total_rooms_count',
            'bedrooms_count',
            'bathrooms_count',
            'kitchens_count',
            'total_area',
            'living_area',
            'amenities'
        ]
        read_only_fields = [
            'owner',
            'lodging_type_choices'
        ]

    def validate(self, data):
        lodging_type = data.get('lodging_type')
        apartment_number = data.get('apartment_number')
        room_number = data.get('room_number')

        if lodging_type == LodgingType.HOUSE and (apartment_number or room_number):
            raise serializers.ValidationError(
                {
                    'apartment_number': 'The apartment number is not required for detached house.',
                    'room_number': 'The room number is not required for detached house.'
                }
            )

        if lodging_type == LodgingType.APARTMENT and (not apartment_number or room_number):
            raise serializers.ValidationError(
                {
                    'apartment_number': 'The apartment number is required for apartment.',
                    'room_number': 'The room number is not required for apartment.'
                }
            )

        if lodging_type == LodgingType.COMMUNAL and (not apartment_number or not room_number):
            raise serializers.ValidationError(
                {
                    'apartment_number': 'The apartment number is required for communal apartment.',
                    'room_number': 'The room number is required for communal apartment.'
                }
            )

        return data
