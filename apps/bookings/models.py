from django.db import models
from django.db.models import Q, F
from django.conf import settings
from django.core.validators import MinValueValidator

from decimal import Decimal

from apps.core.models import UniqueIDModel, TimeStampModel


class Booking(UniqueIDModel, TimeStampModel):

    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        RESERVED = "reserved", "Reserved"
        CANCELED = "canceled", "Canceled"
        OCCUPIED = "occupied", "Occupied"
        ENDED = "ended", "Ended"

    listing = models.ForeignKey('listings.Listing', related_name='bookings', on_delete=models.PROTECT,
                                verbose_name='listing', help_text='The listing this booking belongs to.')
    lessee = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='bookings', on_delete=models.PROTECT,
                               verbose_name='lessee', help_text='The user who books this listing.')
    check_in = models.DateField(verbose_name='check-in date')
    check_out = models.DateField(verbose_name='check-out date')
    status = models.CharField(max_length=20, choices=Status, default=Status.REQUESTED,
                              verbose_name='booking status')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2,
                                      validators=[MinValueValidator(Decimal('0.01'))],
                                      verbose_name='total booking cost')
    lessor_comment = models.TextField(max_length=300, blank=True, default='',
                                      verbose_name='lessor comment',
                                      help_text='A comment left by a potential lessee when accepting or declining a booking request.')
    lessee_comment = models.TextField(max_length=300, blank=True, default='',
                                      verbose_name='lessee comment',
                                      help_text='A comment left by a potential lessee when creating a booking request.')

    class Meta:
        db_table = 'bookings'
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ('-check_in',)
        constraints = [
            models.CheckConstraint(
                condition=Q(check_out__gt=F('check_in')),
                name='booking_checkout_after_checkin'
            )
        ]
