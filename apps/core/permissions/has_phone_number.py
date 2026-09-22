from rest_framework import permissions

class HasPhoneNumber(permissions.BasePermission):
    message = "To perform this action, a phone number must be specified in your profile."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.phone_number
        )
