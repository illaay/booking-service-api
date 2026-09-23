from django.db import models
from django.utils import timezone

class SoftDeleteQuerySet(models.QuerySet):
    """
    Custom QuerySet that intercepts delete operations to perform soft updates.
    """
    def delete(self) -> int:
        return self.update(deleted_at=timezone.now())

    def hard_delete(self) -> tuple:
        return super().delete()


class SoftDeleteManager(models.Manager):
    """
    Model manager enforcing soft deletion filtering across database lookups.
    """
    def get_queryset(self) -> SoftDeleteQuerySet:
        return SoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)

    def all_with_deleted(self) -> SoftDeleteQuerySet:
        return SoftDeleteQuerySet(self.model, using=self._db)
