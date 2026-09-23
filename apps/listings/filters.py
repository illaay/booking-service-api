import django_filters
from apps.listings.models import Listing


class ListingFilter(django_filters.FilterSet):
    """
    Filter set configuration for the Listing model.

    Enables extensive lookup options including geographical queries on the linked
    property, minimum and maximum ranges for rental metrics, room capacities,
    and distinct accommodation classification tags.
    """
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')

    country = django_filters.CharFilter(field_name='property__country', lookup_expr='icontains')
    state = django_filters.CharFilter(field_name='property__state', lookup_expr='icontains')
    city = django_filters.CharFilter(field_name='property__city', lookup_expr='icontains')

    rooms_min = django_filters.NumberFilter(field_name='property__total_rooms_count', lookup_expr='gte')
    rooms_max = django_filters.NumberFilter(field_name='property__total_rooms_count', lookup_expr='lte')

    price_min = django_filters.NumberFilter(field_name='price_per_night', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price_per_night', lookup_expr='lte')

    lodging_type = django_filters.ChoiceFilter(field_name='property__lodging_type')

    class Meta:
        model = Listing
        fields = [
            'title',
            'country',
            'state',
            'city',
            'rooms_min',
            'rooms_max',
            'price_min',
            'price_max',
            'lodging_type'
        ]
