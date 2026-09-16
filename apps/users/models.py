from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

import uuid

from .services import user_directory_path, normalize_name


class UserManager(BaseUserManager):

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


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    email = models.EmailField(unique=True, verbose_name=_('email address'))
    is_email_verified = models.BooleanField(default=False, verbose_name=_('is email verified'))
    first_name = models.CharField(max_length=50, verbose_name=_('first name'))
    last_name = models.CharField(max_length=50, blank=True, default='', verbose_name=_('last name'))
    phone_number = models.CharField(max_length=16, unique=True, blank=True, default='',
                                    verbose_name=_('phone number'),
                                    help_text=_('Enter in international format, e.g., +1234567890.'))
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_('date of birth'),
                                     help_text=_('Date of Birth in format YYYY-MM-DD'))
    bio = models.CharField(max_length=200, blank=True, default='', verbose_name=_('biography'))
    profile_photo = models.ImageField(upload_to=user_directory_path, null=True,
                                      blank=True, verbose_name=_('profile photo'))
    favorite_listings = models.ManyToManyField('Listing', related_name='favorited_by_users',
                                               blank=True, verbose_name=_('favorite listings'))

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    @property
    def created_at(self):
        return self.date_joined

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    objects = UserManager()

    def save(self, *args, **kwargs):
        if self.first_name:
            self.first_name = normalize_name(self.first_name)
        if self.last_name:
            self.last_name = normalize_name(self.last_name)
        return super().save(*args, **kwargs)

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