from rest_framework import serializers
from apps.properties.models import Property
from apps.core.models import LodgingType

from ..models import Amenity
from .amenities import AmenitiesListSerializer


class PropertyMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = [
            'id',
            'country',
            'state',
            'city',
            'street',
            'building'
        ]
        read_only_fields = fields


class PropertyShortSerializer(PropertyMiniSerializer):
    owner_first_name = serializers.CharField(source='owner.first_name', read_only=True)
    owner_last_name = serializers.CharField(source='owner.last_name', read_only=True)
    owner_phone_number = serializers.CharField(source='owner.phone_number', read_only=True)
    amenities = AmenitiesListSerializer(many=True, read_only=True)

    class Meta(PropertyMiniSerializer.Meta):
        fields = PropertyMiniSerializer.Meta.fields + [
            'apartment_number',
            'room_number',
            'lodging_type',
            'total_rooms_count',
            'bedrooms_count',
            'bathrooms_count',
            'kitchens_count',
            'total_area',
            'living_area',
            'owner_first_name',
            'owner_last_name',
            'owner_phone_number',
            'amenities'
        ]
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        if not request or not request.user.is_authenticated:
            data.pop('owner_phone_number', None)

        return data


class PropertyCreateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    amenities = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Amenity.objects.all(),
        required=False
    )
    lodging_type_display = serializers.CharField(source='get_lodging_type_display', read_only=True)

    class Meta:
        model = Property
        fields = [
            'id',
            'owner',
            'country',
            'state',
            'city',
            'street',
            'building',
            'apartment_number',
            'room_number',
            'lodging_type',
            'lodging_type_display',
            'total_rooms_count',
            'bedrooms_count',
            'bathrooms_count',
            'kitchens_count',
            'total_area',
            'living_area',
            'amenities'
        ]
        read_only_fields = [
            'id',
            'owner',
            'lodging_type_display'
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
