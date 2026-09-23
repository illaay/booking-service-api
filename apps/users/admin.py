from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Administrative interface configuration for the custom User identity model.

    Provides listing filters, search criteria, protection layers for security roles,
    and optimized layout pagination for user profile management.
    """
    list_display = ('id', 'email', 'first_name', 'last_name', 'phone_number', 'is_staff', 'date_joined')
    list_display_links = ('id', 'email')
    ordering = ('-date_joined',)
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    list_filter = ('is_staff', 'is_superuser', 'date_joined')
    list_per_page = 25
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'date_of_birth', 'bio', 'profile_photo')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'first_name', 'last_name', 'phone_number', 'date_of_birth'),
        }),
    )
