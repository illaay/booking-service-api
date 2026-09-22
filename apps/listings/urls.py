from rest_framework import routers

from .views import ListingViewSet


router = routers.SimpleRouter()

router.register(r'listings', ListingViewSet, basename='listings')

urlpatterns = router.urls
