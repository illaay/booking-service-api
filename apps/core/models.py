from django.db import models
from django.utils import timezone

import uuid

from .managers import SoftDeleteManager


class UniqueIDModel(models.Model):
    """
    An abstract base class model providing a unique UUID primary key.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampModel(models.Model):
    """
    An abstract base class model tracking instantiation, update, and deletion states.

    Enables automatic record creation/modification dates tracking alongside
    native platform-wide cascading soft-deletion workflows.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='created at',
        help_text='The timestamp when the object instance was originally created.'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='updated at',
        help_text='The timestamp when the object instance was last modified.'
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='deleted at',
        help_text='The timestamp indicating when the object was softly marked as deleted.'
    )

    objects = SoftDeleteManager()

    class Meta:
        abstract = True

    @property
    def is_updated(self) -> bool:
        return self.created_at < self.updated_at

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def delete(self, *args, **kwargs) -> tuple:
        self.deleted_at = timezone.now()
        self.save()
        return 1, {self._meta.label: 1}

    def hard_delete(self, *args, **kwargs) -> tuple:
        return super().delete(*args, **kwargs)


class LodgingType(models.TextChoices):
    HOUSE = 'house', 'Detached house'
    APARTMENT = 'apartment', 'Apartment'
    COMMUNAL = 'communal', 'Communal apartment'
