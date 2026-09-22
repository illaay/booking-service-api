from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.core.models import UniqueIDModel, TimeStampModel


class Review(UniqueIDModel, TimeStampModel):

    listing = models.ForeignKey('listings.Listing', related_name='reviews', on_delete=models.CASCADE)
    review = models.TextField(max_length=500, blank=True)
    commentator = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='comments', on_delete=models.CASCADE
    )
    rating = models.PositiveIntegerField(
        default=5, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        db_table = 'reviews'
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(
                fields=('listing', 'commentator'),
                name='unique_listing_commentator'
            )
        ]
