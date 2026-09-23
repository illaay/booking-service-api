from rest_framework import permissions

class HasPhoneNumber(permissions.BasePermission):
    """
    Permission class ensuring the request user has a validated phone number.

    Rejects incoming execution requests if the profile phone parameter is empty
    or missing.
    """
    message = "To perform this action, a phone number must be specified in your profile."

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.phone_number
        )
