from rest_framework import serializers

from apps.properties.models import Property
from ..models import Listing
from .listing_photos import ListingPhotoSerializer
from apps.properties.serializers.properties import PropertyMiniSerializer, PropertyShortSerializer
from apps.reviews.serializers.reviews import ReviewDetailSerializer


class ListingListSerializer(serializers.ModelSerializer):
    """
    Serializer for a high-level summary representation of rental listings.

    Exposes aggregate feedback figures, minimal physical address location context,
    and associated thumbnail media galleries for index screens.
    """
    property = PropertyMiniSerializer()
    photos = ListingPhotoSerializer(many=True)
    avg_rating = serializers.FloatField()

    class Meta:
        model = Listing
        fields = [
            'id',
            'title',
            'price_per_night',
            'property',
            'avg_rating',
            'photos'
        ]
        read_only_fields = fields


class ListingDetailSerializer(ListingListSerializer):
    """
    Granular model serializer expanding extensive data fields for a single Listing.

    Pulls exhaustive property infrastructure metrics, comprehensive amenity lists,
    operational status indicators, and an embedded collection of customer reviews.
    """
    property = PropertyShortSerializer()
    reviews = ReviewDetailSerializer(many=True)

    class Meta(ListingListSerializer.Meta):
        model = Listing
        fields = ListingListSerializer.Meta.fields + [
            'is_active',
            'description',
            'max_guests',
            'min_rental_days',
            'reviews'
        ]
        read_only_fields = fields


class ListingCreateSerializer(serializers.ModelSerializer):
    """
    Model serializer handling strict validation rules for creating and modifying Listings.

    Dynamically binds validation criteria during initial startup routines to protect
    property boundaries and restrict target inputs to verified owner assets.
    """
    property = serializers.PrimaryKeyRelatedField(queryset=Property.objects.none())

    class Meta:
        model = Listing
        fields = [
            'title',
            'description',
            'property',
            'price_per_night',
            'max_guests',
            'min_rental_days',
            'is_active'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')

        if request and request.user and request.user.is_authenticated:
            self.fields['property'].queryset = Property.objects.filter(
                owner=request.user,
                is_verified=True
            )
