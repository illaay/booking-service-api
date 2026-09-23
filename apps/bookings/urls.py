from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import BookingViewSet


router = SimpleRouter()
router.register(r'', BookingViewSet, basename='bookings')

urlpatterns = [
    path('', include(router.urls))
]
