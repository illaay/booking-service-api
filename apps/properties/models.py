from django.db import models
from django.db.models import Q, F
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from decimal import Decimal

from apps.core.models import UniqueIDModel, TimeStampModel, LodgingType


class Property(UniqueIDModel, TimeStampModel):
    """
    Represents physical real estate infrastructure.

    Stores address data, internal structural layout boundaries, area capacities,
    assigned comfort amenities, and host registration details.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="properties", on_delete=models.CASCADE,
        verbose_name='owner', help_text='The user who owns and manages this real estate asset.'
    )
    # regulated by the administrator (User with is_staff = True)
    # after a theoretical document verification process
    is_verified = models.BooleanField(
        default=False, verbose_name='is verified',
        help_text='Indicates if the property documents have been verified by a platform staff member.'
    )
    country = models.CharField(max_length=50, verbose_name='country', help_text='The country where the property is located.')
    state = models.CharField(max_length=50, verbose_name='state', help_text='The state, region, or province of the property.')
    city = models.CharField(max_length=50, verbose_name='city', help_text='The city or town location.')
    street = models.CharField(max_length=50, verbose_name='street', help_text='The street name or equivalent public address route.')
    building = models.CharField(max_length=10, verbose_name='building', help_text='The building number or structure identifier.')
    # For apartments.
    apartment_number = models.CharField(max_length=7, blank=True, default='', verbose_name='apartment number', help_text='The unique apartment number inside the structure.')
    # For communal apartments.
    room_number = models.CharField(max_length=7, blank=True, default='', verbose_name='room number', help_text='The specific room identifier within a communal apartment configuration.')
    lodging_type = models.CharField(
        max_length=20,
        choices=LodgingType,
        default=LodgingType.APARTMENT,
        verbose_name='lodging type',
        help_text='The structural category classification of the residence.'
    )
    total_rooms_count = models.PositiveIntegerField(
        validators=[MinValueValidator(3), MaxValueValidator(10)],
        verbose_name='total rooms count',
        help_text='Total capacity counter of all non-service rooms.'
    )
    bedrooms_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)],
        verbose_name='bedrooms count',
        help_text='Total count of dedicated sleeping rooms.'
    )
    bathrooms_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        verbose_name='bathrooms count',
        help_text='Total count of functional sanitation restrooms.'
    )
    kitchens_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        verbose_name='kitchens count',
        help_text='Total count of operational cooking areas.'
    )
    total_area = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('1.00'))],
        verbose_name='total area', help_text='The gross layout area of the property measured in square units.'
    )
    living_area = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('1.00'))],
        verbose_name='living area', help_text='The net functional residential living section area measured in square units.'
    )
    amenities = models.ManyToManyField('Amenity', related_name='properties', verbose_name='amenities', help_text='Comfort utilities provided on-site.')

    def __str__(self) -> str:
        address = f"{self.street}, {self.building}"

        if self.apartment_number:
            address += f", apt. {self.apartment_number}"
        if self.room_number:
            address += f", room {self.room_number}"

        return f"{self.city}, {address}"

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"city={self.city} "
            f"street={self.street} "
            f"building={self.building} "
            f"lodging_type={self.lodging_type}>"
        )

    class Meta:
        db_table = 'properties'
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
        ordering = ('-created_at',)
        constraints = [
            models.CheckConstraint(
                condition=(
                        models.Q(
                            lodging_type=LodgingType.HOUSE,
                            apartment_number='',
                            room_number='',
                        )
                        | models.Q(
                    lodging_type=LodgingType.APARTMENT,
                    apartment_number__gt='',
                    room_number='',
                )
                        | models.Q(
                    lodging_type=LodgingType.COMMUNAL,
                    apartment_number__gt='',
                    room_number__gt='',
                )
                ),
                name='valid_property_lodging_type',
            ),
            models.CheckConstraint(
                condition=Q(living_area__lt=F('total_area')),
                name='living_area_is_smaller_than_total_area',
            ),
            models.UniqueConstraint(
                fields=[
                    'country',
                    'state',
                    'city',
                    'street',
                    'building',
                    'apartment_number',
                    'room_number',
                ],
                name='unique_property_address',
            )
        ]


class Amenity(UniqueIDModel, TimeStampModel):
    """
    Represents an on-site utility, comfort feature, or appliance item.
    """
    name = models.CharField(max_length=50, unique=True, verbose_name='name', help_text='The descriptive unique name of the amenity item.')

    class Meta:
        db_table = 'amenities'
        verbose_name = 'Amenity'
        verbose_name_plural = 'Amenities'
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: id={self.id}, name={self.name}>"
