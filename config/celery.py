import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('rent_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update-booking-statuses-every-hour': {
        'task': 'apps.bookings.tasks.update_booking_statuses',
        'schedule': crontab(minute=0),
    },
}
