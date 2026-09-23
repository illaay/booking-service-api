from rest_framework import serializers

from ..models import Amenity


class AmenitiesListSerializer(serializers.ModelSerializer):
    """
    Serializer for a concise summary representation of comfort Amenities.

    Exposes the system primary identification tracking keys along with the
    public descriptive names for UI presentation listings.
    """
    class Meta:
        model = Amenity
        fields = ['id', 'name']
        read_only_fields = fields
