from django.urls import path, include
from rest_framework import routers

from .views import UserViewSet


router = routers.SimpleRouter()
router.register('', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls))
]

