from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import ListingViewSet


router = SimpleRouter()
router.register(r'', ListingViewSet, basename='listings')

urlpatterns = [
    path('', include(router.urls))
]
