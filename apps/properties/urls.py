from rest_framework import routers

from .views import PropertyCreateViewSet


router = routers.SimpleRouter()
router.register('add', PropertyCreateViewSet, basename='add-property')

urlpatterns = router.urls
