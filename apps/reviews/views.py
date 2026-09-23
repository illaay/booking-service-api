from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Review
from .serializers.reviews import ReviewDetailSerializer, ReviewCreateSerializer


class ReviewViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    queryset = Review.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ReviewCreateSerializer
        return ReviewDetailSerializer

    def get_queryset(self):
        queryset = Review.objects.select_related('commentator')

        listing_id = self.request.query_params.get('listing')
        if listing_id:
            queryset = queryset.filter(listing_id=listing_id)
        return queryset

    @action(detail=False, methods=['get'], url_path='my', permission_classes=[IsAuthenticated])
    def my_reviews(self, request):
        queryset = self.get_queryset().filter(commentator=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        review = self.get_object()
        if review.commentator != request.user:
            return Response({"detail": "You are not the author of this review."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
