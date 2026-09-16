from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from apps.core.models import UniqueIDModel, TimeStampModel


class Listing(UniqueIDModel, TimeStampModel):

    title = models.CharField(max_length=100, validators=[MinLengthValidator(5)],
                             verbose_name=_('listing title'))
    description = models.TextField(max_length=1000, blank=True, default='',
                                   verbose_name=_('listing description'))
    property = models.OneToOneField('Property', on_delete=models.CASCADE, related_name='listing',
                                    verbose_name=_('property'),
                                    help_text=_('Property associated with the listing.'))
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2,
                                          verbose_name=_('price per night'))
    max_guests = models.PositiveIntegerField(default=0, verbose_name=_('maximum guests'),
                                             help_text=_('Maximum number of guests allowed to stay.'))
    min_rental_days = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)],
                                                  verbose_name=_('minimum days'),
                                                  help_text=_('The minimum number of days required for a booking.'))

    class Meta:
        db_table = 'listings'
        verbose_name = 'Listing'
        verbose_name_plural = 'Listings'
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=('title',), name='listing_title_index')
        ]


class ListingPhoto(UniqueIDModel, TimeStampModel):

    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='photos',
                                verbose_name=_('listing'))
    photo = models.ImageField(upload_to='listing_photos', verbose_name=_('photo'))
    photo_sequence_number = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name=_('photo sequence number'),
        help_text=_('The position of the photo in the listing gallery.')

    )

    class Meta:
        db_table = 'listing_photos'
        verbose_name = 'Listing Photo'
        verbose_name_plural = 'Listing Photos'
        constraints = [
            models.UniqueConstraint(
                fields=('listing', 'photo_sequence_number'),
                name='unique_listing_photo_sequence_number',
            )
        ]
