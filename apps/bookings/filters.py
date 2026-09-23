import django_filters
from apps.bookings.models import Booking


class BookingFilter(django_filters.FilterSet):
    """
    Filter set configuration for the Booking model.

    Allows complex query parameters lookup including dynamic financial ranges,
    status filtering, and booking date ranges.
    """
    listing_title = django_filters.CharFilter(field_name='listing__title', lookup_expr='icontains')

    amount_min = django_filters.NumberFilter(field_name='amount_paid', lookup_expr='gte')
    amount_max = django_filters.NumberFilter(field_name='amount_paid', lookup_expr='lte')

    status = django_filters.ChoiceFilter(choices=Booking.Status.choices)

    check_in_after = django_filters.DateFilter(field_name='check_in', lookup_expr='gte')
    check_out_before = django_filters.DateFilter(field_name='check_out', lookup_expr='lte')

    class Meta:
        model = Booking
        fields = [
            'listing_title',
            'amount_min',
            'amount_max',
            'status',
            'check_in_after',
            'check_out_before'
        ]
