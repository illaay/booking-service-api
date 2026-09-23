from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

import uuid

from .managers import UserManager
from .services import user_directory_path, normalize_name


class User(AbstractUser):
    """
    Custom user identity model substitution using email authentication tracking.

    Stores system permissions, personal demographics parameters, verified digital
    contact routes, visual media references, and user bookmark collections.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    email = models.EmailField(unique=True, verbose_name=_('email address'),
                              help_text=_('The unique primary electronic mail address used for authentication.'))
    is_email_verified = models.BooleanField(default=False, verbose_name=_('is email verified'), help_text=_(
        'Designates whether the electronic mail identifier has been verified.'))
    first_name = models.CharField(max_length=50, verbose_name=_('first name'),
                                  help_text=_('The given name of the identity.'))
    last_name = models.CharField(max_length=50, blank=True, default='', verbose_name=_('last name'),
                                 help_text=_('The family name of the identity.'))
    phone_number = models.CharField(max_length=16, unique=True, blank=True, default='',
                                    verbose_name=_('phone number'),
                                    help_text=_(
                                        'Enter in international format, e.g., +1234567890. Visible in listings if you are the host, and visible to both parties within a booking confirmation.'))
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_('date of birth'),
                                     help_text=_('Date of Birth in format YYYY-MM-DD'))
    bio = models.CharField(max_length=200, blank=True, default='', verbose_name=_('biography'),
                           help_text=_('A short textual description or introductory notes of the profile.'))
    profile_photo = models.ImageField(upload_to=user_directory_path, null=True,
                                      blank=True, verbose_name=_('profile photo'),
                                      help_text=_('An image asset reference representing the digital avatar.'))
    favorite_listings = models.ManyToManyField('listings.Listing', related_name='favorited_by_users',
                                               blank=True, verbose_name=_('favorite listings'),
                                               help_text=_('Collection of bookmarked listings saved by the user.'))

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    @property
    def created_at(self) -> models.DateTimeField:
        return self.date_joined

    @property
    def is_updated(self) -> bool:
        return self.date_joined < self.updated_at

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    objects = UserManager()

    def save(self, *args, **kwargs):
        if self.first_name:
            self.first_name = normalize_name(self.first_name)
        if self.last_name:
            self.last_name = normalize_name(self.last_name)
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> tuple:
        """
        Softly delete the user profile by setting the deletion timestamp.
        """
        from django.utils import timezone
        self.deleted_at = timezone.now()
        self.save()
        return 1, {self._meta.label: 1}

    def hard_delete(self, *args, **kwargs) -> tuple:
        """
        Permanently remove the user record from the database.
        """
        return super().delete(*args, **kwargs)

    def __str__(self) -> str:
        return self.email

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: id={self.id}, email={self.email}, is_staff={self.is_staff}>"

    class Meta:
        db_table = 'users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ('-date_joined',)
        constraints = [
            models.CheckConstraint(
                condition=Q(phone_number__contains='+') | Q(phone_number=''),
                name='phone_number_contains_plus_symbol'
            ),
        ]
