from django.contrib import admin
from .models import Listing


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    """
    Administrative interface configuration for the Listing model.

    Provides visualization filters, full-text search parameters, read-only
    operational counters protection, and customized pagination layouts.
    """
    list_display = ('id', 'title', 'price_per_night', 'max_guests', 'is_active', 'views_count', 'created_at')
    list_display_links = ('id', 'title')
    list_filter = ('is_active', 'created_at')
    ordering = ('created_at',)
    search_fields = ('title', 'property__city')
    readonly_fields = ('id', 'views_count', 'created_at', 'updated_at', 'deleted_at')
    list_per_page = 25
