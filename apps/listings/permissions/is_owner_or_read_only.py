from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to restrict write operations to property owners.

    Allows safe HTTP methods (GET, HEAD, OPTIONS) for any request, but guards
    destructive or modification requests by validating user identity against
    the underlying property ownership.
    """
    message = 'You can only edit your own listings.'

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.property.owner == request.user
