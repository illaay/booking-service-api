from rest_framework import serializers

from ..models import Amenity


class AmenitiesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['id', 'name']
        read_only_fields = fields