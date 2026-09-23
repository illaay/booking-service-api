from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Property
from .serializers.properties import PropertyCreateSerializer, PropertyShortSerializer

class PropertyViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing real estate infrastructure assets.

    Provides secure workflows for property registration, list retrieval,
    and profile-isolated space inventory ownership management.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Property.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return PropertyCreateSerializer
        return PropertyShortSerializer

    @action(detail=False, methods=['get'], url_path='my')
    def my_properties(self, request):
        """
        Retrieve a collection of all registered properties belonging to the current host.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
