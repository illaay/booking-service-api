from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from .models import Property
from .serializers.properties import PropertyCreateSerializer

class PropertyCreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertyCreateSerializer
    permission_classes = [IsAuthenticated]
