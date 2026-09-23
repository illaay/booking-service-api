from django.urls import path, include
from rest_framework import routers

from .views import ListingViewSet


router = routers.SimpleRouter()

router.register(r'', ListingViewSet, basename='listings')

urlpatterns = [
    path('', include(router.urls))
]
