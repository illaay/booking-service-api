from django.db import models
from django.utils import timezone

import uuid


class UniqueIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    # def delete(self, *args, **kwargs):
    #     self.deleted_at = timezone.now()
    #     self.save()
    #     return 1, {self._meta.label: 1}


class LodgingType(models.TextChoices):
    HOUSE = 'house', 'Detached house'
    APARTMENT = 'apartment', 'Apartment'
    COMMUNAL = 'communal', 'Communal apartment'
