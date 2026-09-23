from django.contrib import admin

from .models import Property
from .models import Amenity


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """
    Administrative interface configuration for the Property model.

    Provides listing filters, search parameters, custom verification actions,
    and layout optimization for backend properties management.
    """
    list_display = ('id', 'owner', 'country', 'city', 'street', 'building', 'lodging_type', 'is_verified', 'created_at')
    list_display_links = ('id', 'owner')
    list_filter = ('is_verified', 'lodging_type', 'country', 'city')
    ordering = ('-created_at',)
    search_fields = ('owner__email', 'city', 'street')
    readonly_fields = ('id', 'created_at', 'updated_at', 'deleted_at')
    actions = ['approve_properties']
    list_per_page = 25

    @admin.action(description='Verify selected properties')
    def approve_properties(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"Successfully verified properties: {updated}.")


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    """
    Administrative interface configuration for the Amenity lookup model.

    Provides a clean interface for editing, creating, and tracking system-wide
    comfort utilities and appliance tags.
    """
    list_display = ('id', 'name', 'created_at')
    ordering = ('-created_at',)
    search_fields = ('name',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'deleted_at')
    list_per_page = 25
