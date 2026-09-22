from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import PropertyViewSet

router = SimpleRouter()
router.register(r'', PropertyViewSet, basename='properties')

urlpatterns = [
    path('', include(router.urls)),
]
