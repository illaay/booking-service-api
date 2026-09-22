from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from datetime import date, timedelta

from ..models import Booking
from apps.listings.serializers.listings import ListingListSerializer


class BookingListSerializer(serializers.ModelSerializer):
    listing = ListingListSerializer()

    class Meta:
        model = Booking
        fields = [
            'id',
            'listing',
            'check_in',
            'check_out',
            'status',
            'amount_paid',
            'created_at'
        ]
        read_only_fields = fields


class BookingDetailSerializer(serializers.ModelSerializer):
    listing = ListingListSerializer()
    lessee_first_name = serializers.CharField(source='lessee.first_name')
    lessee_last_name = serializers.CharField(source='lessee.last_name')
    lessor_first_name = serializers.CharField(source='listing.property.owner.first_name')
    lessor_last_name = serializers.CharField(source='listing.property.owner.last_name')

    class Meta:
        model = Booking
        fields = [
            'id',
            'listing',
            'lessee_first_name',
            'lessee_last_name',
            'lessor_first_name',
            'lessor_last_name',
            'check_in',
            'check_out',
            'status',
            'amount_paid',
            'lessee_comment',
            'lessor_comment',
            'created_at'
        ]
        read_only_fields = fields


class BookingActionSerializer(serializers.ModelSerializer):
    lessor_comment = serializers.CharField(required=False)

    class Meta:
        model = Booking
        fields = ['lessor_comment']


class BookingCreateSerializer(serializers.ModelSerializer):
    lessee = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Booking
        fields = [
            'id',
            'listing',
            'lessee',
            'check_in',
            'check_out',
            'lessee_comment',
            'amount_paid'
        ]
        read_only_fields = ['id', 'lessee']

    def validate(self, attrs):
        check_in = attrs.get('check_in')
        check_out = attrs.get('check_out')
        listing = attrs.get('listing')
        request = self.context.get('request')

        if check_in < date.today():
            raise serializers.ValidationError({'check_in': _('Дата заезда не может быть в прошлом.')})

        if check_out <= check_in:
            raise serializers.ValidationError({'check_out': _('Check-out date must be after the check-in date.')})

        if check_in > (date.today() + timedelta(days=180)):
            raise serializers.ValidationError({'check_in': 'Check-in date cannot be more than 180 days in the future.'})

        min_days = listing.min_rental_days
        rental_days = (check_out - check_in).days
        if rental_days < min_days:
            raise serializers.ValidationError(
                {'detail': _(f'Minimum rental period for this listing is {min_days} days.')})

        if attrs.get('amount_paid') <= 0:
            raise serializers.ValidationError({'amount_paid': _('Proposed price must be greater than zero.')})

        if request and request.user == listing.property.owner:
            raise serializers.ValidationError({'detail': _('You cannot book your own listing.')})

        return attrs
