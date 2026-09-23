from celery import shared_task
from django.utils import timezone
from apps.bookings.models import Booking

@shared_task
def update_booking_statuses() -> str:
    """
    Periodically update the execution lifecycle status of active bookings.

    Transitions reservations from 'OCCUPIED' to 'ENDED' once the check-out date
    has passed, and from 'RESERVED' to 'OCCUPIED' when the check-in date arrives.

    :return: Summary statement of modified booking records count.
    :rtype: str
    """
    today = timezone.now().date()

    check_out_updated = Booking.objects.filter(
        status=Booking.Status.OCCUPIED,
        check_out__lt=today
    ).update(status=Booking.Status.ENDED)

    check_in_updated = Booking.objects.filter(
        status=Booking.Status.RESERVED,
        check_in__lte=today,
        check_out__gt=today
    ).update(status=Booking.Status.OCCUPIED)

    return f"Checked in: {check_in_updated}, Checked out: {check_out_updated}."
