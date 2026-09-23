from django.contrib.auth import get_user_model
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers.users import UserCreateSerializer, UserProfileSerializer, UserMeSerializer


User = get_user_model()


class UserViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    API ViewSet for processing account identities and profile orchestration.

    Handles public registration onboarding workflows, secure profile settings
    management via self-isolated endpoints, and strict deletion constraint evaluations.
    """

    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'register':
            return UserCreateSerializer

        elif self.action == 'me':
            return UserMeSerializer

        return UserProfileSerializer

    def get_permissions(self):
        if self.action in ['register', 'retrieve']:
            return [AllowAny()]

        return [IsAuthenticated()]

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        """
        Register a new user identity in the system database.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get', 'put', 'patch', 'delete'], url_path='me')
    def me(self, request):
        """
        Perform read, update, or soft-deletion routines on the currently authenticated session profile.
        """
        user = request.user

        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        if request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(
                user, data=request.data, partial=(request.method == 'PATCH')
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        if request.method == 'DELETE':
            try:
                user.delete()
            except ProtectedError:
                return Response(
                    {
                        'detail': 'It is not possible to delete the profile because there are pending bookings.'
                    },
                    status=status.HTTP_409_CONFLICT
                )

            return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a public summary of a specific user or redirect to the full self profile.
        """
        url_pk = self.kwargs.get('pk')
        current_user = request.user

        if current_user.is_authenticated and str(url_pk) == str(current_user.pk):
            return HttpResponseRedirect(reverse('users-me'))

        return super().retrieve(request, *args, **kwargs)
