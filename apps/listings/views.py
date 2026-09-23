from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Prefetch, Avg, F
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from apps.reviews.models import Review
from .models import Listing, ListingPhoto
from apps.listings.serializers.listings import ListingListSerializer, ListingDetailSerializer, ListingCreateSerializer
from .permissions.has_confirmed_property import HasConfirmedProperty
from .permissions.is_owner_or_read_only import IsOwnerOrReadOnly
from apps.core.permissions.has_phone_number import HasPhoneNumber
from .filters import ListingFilter


class ListingViewSet(viewsets.ModelViewSet):
    """
    API ViewSet managing the complete lifecycle of rental advertisements.

    Exposes public discovery feeds, transactional publishing forms for property
    owners, multi-layered data aggregation, atomic interaction updates,
    and granular object security barriers.
    """

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ListingFilter
    ordering_fields = ['price_per_night', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Listing.objects.annotate(
            avg_rating=Avg('reviews__rating'),
        ).select_related(
            'property', 'property__owner'
        ).prefetch_related(
            'property__amenities'
        )

        if self.action == 'list':
            queryset = queryset.filter(is_active=True)
            main_photo_queryset = ListingPhoto.objects.filter(photo_sequence_number=1)
            return queryset.prefetch_related(
                Prefetch('photos', queryset=main_photo_queryset)
            )

        return queryset.prefetch_related(
            'photos',
            Prefetch('reviews', queryset=Review.objects.select_related('commentator'))
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return ListingListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ListingCreateSerializer
        return ListingDetailSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        if self.action == 'create':
            return [IsAuthenticated(), HasPhoneNumber(), HasConfirmedProperty()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=['get'], url_path='my', permission_classes=[IsAuthenticated])
    def my_listings(self, request):
        """
        Retrieve all rental advertisements belonging to the authenticated host user.
        """
        queryset = self.get_queryset().filter(property__owner=request.user)
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve deep descriptive metrics of an individual listing and atomically increment views tracker.
        """
        instance = self.get_object()
        Listing.objects.filter(pk=instance.pk).update(views_count=F('views_count') + 1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
