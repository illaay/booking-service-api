from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import ReviewViewSet


router = SimpleRouter()

router.register(r'reviews', ReviewViewSet, basename='reviews')

urlpatterns = [
    path('', include(router.urls))
]