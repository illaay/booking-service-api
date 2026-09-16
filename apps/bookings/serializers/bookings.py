from rest_framework import serializers
from bookings.models import Booking


class BookingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['listing', 'lessee', 'check_in', 'check_out', 'status', 'amount_paid']

