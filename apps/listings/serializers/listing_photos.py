from rest_framework import serializers

from ..models import ListingPhoto


class ListingPhotoSerializer(serializers.ModelSerializer):
    """
    Serializer for managing visual media assets associated with rental listings.

    Handles the identification link, the direct source path of the image file,
    and its layout display priority inside the public presentation gallery.
    """

    class Meta:
        model = ListingPhoto
        fields = ['id', 'photo', 'photo_sequence_number']
