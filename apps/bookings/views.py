from django.db.models import Avg, Prefetch
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from datetime import timedelta, date

from apps.listings.models import Listing
from .models import Booking
from .serializers.bookings import (
    BookingListSerializer,
    BookingDetailSerializer,
    BookingCreateSerializer,
    BookingActionSerializer)
from apps.core.permissions.has_phone_number import HasPhoneNumber


class BookingViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin
):

    queryset = Booking.objects.all()
    permission_classes = [IsAuthenticated, HasPhoneNumber]

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        if self.action == 'retrieve':
            return BookingDetailSerializer
        if self.action in ['accept_booking', 'reject_booking']:
            return BookingActionSerializer
        return BookingListSerializer

    def get_queryset(self):
        optimized_listing_queryset = Listing.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).select_related('property', 'property__owner').prefetch_related('property__amenities')

        return Booking.objects.select_related(
            'lessee'
        ).prefetch_related(
            Prefetch('listing', queryset=optimized_listing_queryset),
            'listing__photos'
        )

    @action(detail=False, methods=['get'], url_path='my-trips')
    def my_trips(self, request):
        queryset = self.get_queryset().filter(lessee=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='my-orders')
    def my_orders(self, request):
        queryset = self.get_queryset().filter(listing__property__owner=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        booking = self.get_queryset().filter(id=kwargs.get('pk')).first()

        if not booking:
            return Response({"detail": _("Booking not found.")}, status=status.HTTP_404_NOT_FOUND)

        if request.user != booking.lessee and request.user != booking.listing.property.owner:
            return Response({"detail": _("You don't have permission to view this booking.")},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='accept')
    def accept_booking(self, request, pk=None):
        booking = self.get_object()

        if request.user != booking.listing.property.owner:
            return Response({"detail": _("You are not the owner of this property.")}, status=status.HTTP_403_FORBIDDEN)

        if booking.status != Booking.Status.REQUESTED:
            return Response({"detail": _("Only requests with the Requested status can be confirmed.")},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking.status = Booking.Status.RESERVED
        booking.save()

        return Response({"status": _("Booking successfully confirmed (Reserved).")})

    @action(detail=True, methods=['post'], url_path='reject')
    def reject_booking(self, request, pk=None):
        booking = self.get_object()

        if request.user != booking.listing.property.owner:
            return Response({"detail": _("You are not the owner of this property.")}, status=status.HTTP_403_FORBIDDEN)

        if booking.status != Booking.Status.REQUESTED:
            return Response({"detail": _("This request has already been processed or cancelled.")}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking.status = Booking.Status.CANCELED
        booking.save()

        return Response({"status": _("Booking declined by the host (Canceled).")})

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_booking(self, request, pk=None):
        booking = self.get_object()

        if request.user != booking.lessee and request.user != booking.listing.property.owner:
            return Response({"detail": _("You do not have permission to cancel this booking.")},
                            status=status.HTTP_403_FORBIDDEN)

        if booking.status in [Booking.Status.CANCELED, Booking.Status.ENDED]:
            return Response({"detail": _("This booking cannot be cancelled because it has already been completed or cancelled.")},
                            status=status.HTTP_400_BAD_REQUEST)

        if date.today() > booking.check_in - timedelta(days=1):
            return Response({"detail": _("Booking cannot be cancelled less than a day before the check-in date.")})


        booking.status = Booking.Status.CANCELED
        booking.save()

        return Response({"status": "Booking successfully cancelled."})
