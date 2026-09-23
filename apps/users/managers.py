from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom manager for the User model enforcing soft deletion filtering.
    """

    def get_queryset(self):
        """
        Return only active, non-deleted user instances by default.
        """
        # Импортируем локально, чтобы избежать круговых импортов
        from apps.core.managers import SoftDeleteQuerySet
        return SoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)

    def all_with_deleted(self):
        """
        Return all users, including those softly marked as deleted.
        """
        from apps.core.managers import SoftDeleteQuerySet
        return SoftDeleteQuerySet(self.model, using=self._db)

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
