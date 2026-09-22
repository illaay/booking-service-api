from rest_framework import serializers

from ..models import ListingPhoto


class ListingPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingPhoto
        fields = ['id', 'photo', 'photo_sequence_number']