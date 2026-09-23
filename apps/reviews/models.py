from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.core.models import UniqueIDModel, TimeStampModel


class Review(UniqueIDModel, TimeStampModel):
    """
    Represents a guest review and evaluation for a rental listing.

    Tracks a numerical quality rating and text feedback left by an authenticated
    lessee following a verified transactional booking stay.
    """

    listing = models.ForeignKey('listings.Listing', related_name='reviews', on_delete=models.CASCADE,
                                verbose_name='listing', help_text='The specific rental offer this feedback is submitted for.')
    review = models.TextField(max_length=500, blank=True,
                              verbose_name='review text', help_text='The written testimonial or detailed feedback content.')
    commentator = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='comments', on_delete=models.CASCADE,
        verbose_name='commentator', help_text='The authenticated user who published this review.')
    rating = models.PositiveIntegerField(
        default=5, validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='rating score', help_text='A numerical assessment score evaluated strictly between 1 and 5 stars.'
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

    def __str__(self) -> str:
        return f"Review {self.id} ({self.rating}/5)"

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}: id={self.id}, "
            f"listing_id={self.listing_id}, commentator_id={self.commentator_id}, "
            f"rating={self.rating}>"
        )
