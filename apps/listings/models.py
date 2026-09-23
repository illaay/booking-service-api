from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from apps.core.models import UniqueIDModel, TimeStampModel


class Listing(UniqueIDModel, TimeStampModel):
    """
    Represents a public advertisement or offering for real estate rental.

    Combines physical property data with operational financial constraints,
    minimum stay guidelines, public visibility states, and user interaction metrics.
    """

    title = models.CharField(max_length=100, validators=[MinLengthValidator(5)],
                             verbose_name=_('listing title'), help_text=_('The public promotional title for the rental offer.'))
    description = models.TextField(max_length=1000, blank=True, default='',
                                   verbose_name=_('listing description'), help_text=_('Granular description highlighting rules and benefits of the residence.'))
    property = models.OneToOneField('properties.Property', on_delete=models.CASCADE, related_name='listing',
                                    verbose_name=_('property'),
                                    help_text=_('Property associated with the listing.'))
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2,
                                          verbose_name=_('price per night'), help_text=_('The standard accommodation price for a single night stay.'))
    max_guests = models.PositiveIntegerField(default=0, verbose_name=_('maximum guests'),
                                             help_text=_('Maximum number of guests allowed to stay.'))
    min_rental_days = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)],
                                                  verbose_name=_('minimum days'),
                                                  help_text=_('The minimum number of days required for a booking.'))
    is_active = models.BooleanField(default=True, verbose_name=_('is active'),
                                    help_text=_('Designates whether this listing is visible to the public.'))
    views_count = models.PositiveIntegerField(default=0, verbose_name=_('views count'), help_text=_('Total counter of unique details page lookups.'))

    class Meta:
        db_table = 'listings'
        verbose_name = 'Listing'
        verbose_name_plural = 'Listings'
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=('title',), name='listing_title_index')
        ]

    def __str__(self) -> str:
        return f"{self.title} (${self.price_per_night}/night)"

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}: id={self.id}, "
            f"property_id={self.property_id}, price={self.price_per_night}, "
            f"is_active={self.is_active}>"
        )


class ListingPhoto(UniqueIDModel, TimeStampModel):
    """
    Represents an image asset assigned to a specific rental offer gallery.
    """

    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='photos',
                                verbose_name=_('listing'), help_text=_('The operational rental offer this file is assigned to.'))
    photo = models.ImageField(upload_to='listing_photos', verbose_name=_('photo'), help_text=_('Binary image file containing the visual upload.'))
    photo_sequence_number = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name=_('photo sequence number'),
        help_text=_('The position of the photo in the listing gallery.')
    )

    class Meta:
        db_table = 'listing_photos'
        verbose_name = 'Listing Photo'
        verbose_name_plural = 'Listing Photos'
        ordering = ('photo_sequence_number',)
        constraints = [
            models.UniqueConstraint(
                fields=('listing', 'photo_sequence_number'),
                name='unique_listing_photo_sequence_number',
            )
        ]

    def __str__(self) -> str:
        return f"Photo {self.photo_sequence_number} for Listing {self.listing_id}"

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}: id={self.id}, "
            f"listing_id={self.listing_id}, sequence={self.photo_sequence_number}>"
        )
