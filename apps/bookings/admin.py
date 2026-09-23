from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Administrative interface configuration for the Booking model.

    Provides listing filters, search criteria, read-only fields protection,
    and optimized pagination control for backend administrators.
    """
    list_display = ('id', 'listing', 'lessee', 'check_in', 'check_out', 'status', 'amount_paid')
    list_filter = ('status', 'check_in')
    ordering = ('created_at',)
    search_fields = ('lessee__email', 'listing__title')
    readonly_fields = ('id', 'amount_paid', 'created_at', 'updated_at', 'deleted_at')
    list_per_page = 25
