from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from datetime import date

from ..services import normalize_name


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer providing a public-facing read-only representation of a User profile.

    Exposes basic identity tokens, biography description fields, creation dates,
    and associated visual representation assets.
    """

    class Meta:
        model = get_user_model()
        fields = [
            'id',
            'first_name',
            'last_name',
            'date_joined',
            'bio',
            'profile_photo'
        ]
        read_only_fields = fields


class UserMeSerializer(serializers.ModelSerializer):
    """
    Model serializer dedicated to private profile management routines.

    Enriches the baseline public profile fields with restricted communication parameters
    such as phone metadata, birth logs, and verified security references.
    """

    class Meta(UserProfileSerializer.Meta):
        fields = UserProfileSerializer.Meta.fields + [
            'email',
            'phone_number',
            'date_of_birth'
        ]
        read_only_fields = [
            'id',
            'email',
            'date_joined'
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Transactional model serializer handling robust validation routines for registration.

    Enforces mandatory strict corporate policies regarding operational passwords verification,
    minimum acceptable age thresholds, and canonical personal identifier string normalization.
    """
    password = serializers.CharField(required=True, write_only=True)
    date_of_birth = serializers.DateField(required=True)

    class Meta:
        model = get_user_model()
        fields = [
            'first_name',
            'last_name',
            'email',
            'password',
            'date_of_birth',
            'phone_number',
            'bio',
            'profile_photo'
        ]
        read_only_fields = []

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def validate_password(self, value):
        try:
            validate_password(value, user=self.instance)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate_date_of_birth(self, value):
        today = date.today()
        if value > today:
            raise serializers.ValidationError(_('Date of birth cannot be in the future.'))

        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise serializers.ValidationError(_('The user cannot be under 18 years of age.'))
        return value

    def validate_first_name(self, value):
        return normalize_name(value)

    def validate_last_name(self, value):
        return normalize_name(value)
