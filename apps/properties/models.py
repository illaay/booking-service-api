from django.db import models
from django.db.models import Q, F
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from decimal import Decimal

from apps.core.models import UniqueIDModel, TimeStampModel, LodgingType


class Property(UniqueIDModel, TimeStampModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="properties", on_delete=models.CASCADE
    )
    # регулируется администратором (User с is_stuff = True)
    # после теоретической проверки документов
    is_verified = models.BooleanField(default=False)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    building = models.CharField(max_length=10)
    # для квартир
    apartment_number = models.CharField(max_length=7, blank=True, default='')
    # для коммунальных квартир
    room_number = models.CharField(max_length=7, blank=True, default='')
    lodging_type = models.CharField(
        max_length=20,
        choices=LodgingType,
        default=LodgingType.APARTMENT,
    )
    total_rooms_count = models.PositiveIntegerField(
        validators=[MinValueValidator(3), MaxValueValidator(10)]
    )
    bedrooms_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)]
    )
    bathrooms_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)]
    )
    kitchens_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)]
    )
    total_area = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('1.00'))]
    )
    living_area = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('1.00'))]
    )
    amenities = models.ManyToManyField('Amenity', related_name='properties', null=True)

    def __str__(self):
        address = f"{self.street}, {self.building}"

        if self.apartment_number:
            address += f", apt. {self.apartment_number}"
        if self.room_number:
            address += f", room {self.room_number}"

        return f"{self.city}, {address}"

    def __repr__(self):
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
    has_wifi = models.BooleanField(default=False)
    has_bedding = models.BooleanField(default=False)
    has_dishes = models.BooleanField(default=False)
    has_furniture = models.BooleanField(default=False)
    has_washing_machine = models.BooleanField(default=False)
    has_tv = models.BooleanField(default=False)
    has_refrigerator = models.BooleanField(default=False)

    class Meta:
        db_table = 'amenities'
        verbose_name = 'Amenity'
        verbose_name_plural = 'Amenities'
        ordering = ('-created_at',)
