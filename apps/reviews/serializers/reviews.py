from rest_framework import serializers
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from datetime import timedelta

from ..models import Review
from apps.bookings.models import Booking


class ReviewDetailSerializer(serializers.ModelSerializer):
    """
    Detailed model serializer for reading customer feedback and testimonial entries.

    Deconstructs related user structural columns to isolate public identity
    strings alongside computed modification flags.
    """
    commentator_first_name = serializers.CharField(source='commentator.first_name')
    commentator_last_name = serializers.CharField(source='commentator.last_name')

    class Meta:
        model = Review
        fields = [
            'id',
            'commentator_first_name',
            'commentator_last_name',
            'review',
            'commentator',
            'rating',
            'created_at',
            'is_updated'
        ]
        read_only_fields = fields


class ReviewCreateSerializer(serializers.ModelSerializer):
    """
    Transactional creation model serializer for authenticating incoming Reviews.

    Enforces mandatory evaluation criteria, guarding the listing repository from
    unauthorized entries by checking completed temporal rental reservation links.
    """
    commentator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Review
        fields = ['id', 'listing', 'commentator', 'review', 'rating']
        read_only_fields = ['id', 'commentator']

    def validate(self, attrs):
        request = self.context.get('request')
        today = timezone.now().date()

        if self.instance:
            listing = self.instance.listing
            commentator = self.instance.commentator

            if request and commentator != request.user:
                raise serializers.ValidationError({"detail": _("You are not the author of this review.")})
        else:
            listing = attrs.get('listing')
            commentator = attrs.get('commentator')

        recent_booking_exists = Booking.objects.filter(
            listing=listing,
            lessee=commentator,
            status=Booking.Status.ENDED,
            check_out__gte=today - timedelta(days=14),
            check_out__lte=today
        ).exists()

        if not recent_booking_exists:
            raise serializers.ValidationError(
                {"detail": _("You can only leave or edit a review within 14 days after a confirmed stay has ended.")}
            )

        if not self.instance:
            if Review.objects.filter(listing=listing, commentator=commentator).exists():
                raise serializers.ValidationError(
                    {"detail": _("You have already left a review for this listing.")}
                )

        return attrs
