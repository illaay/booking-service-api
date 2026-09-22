from rest_framework import serializers

from apps.properties.models import Property
from ..models import Listing
from .listing_photos import ListingPhotoSerializer
from apps.properties.serializers.properties import PropertyMiniSerializer, PropertyShortSerializer
from apps.reviews.serializers.reviews import ReviewDetailSerializer


class ListingListSerializer(serializers.ModelSerializer):
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
