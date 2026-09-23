from rest_framework import permissions
from apps.properties.models import Property


class HasConfirmedProperty(permissions.BasePermission):
    """
    Permission class checking if the current user owns verified properties.

    Restricts specific creation requests unless an address verification condition
    is completely met in the property registry database.
    """
    message = "You don't have any verified property addresses to create a listing."

    def has_permission(self, request, view) -> bool:
        if request.method == 'POST':
            return Property.objects.filter(
                owner=request.user,
                is_verified=True
            ).exists()

        return True
