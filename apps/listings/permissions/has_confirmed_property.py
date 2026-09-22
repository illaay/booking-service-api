from rest_framework import permissions
from apps.properties.models import Property


class HasConfirmedProperty(permissions.BasePermission):
    message = "You don't have any verified property addresses to create a listing."

    def has_permission(self, request, view):
        if request.method == 'POST':
            return Property.objects.filter(
                owner=request.user,
                is_verified=True
            ).exists()

        return True
