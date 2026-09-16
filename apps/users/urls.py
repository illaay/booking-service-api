from rest_framework import routers

from .views import UserRegisterViewSet


router = routers.SimpleRouter()
router.register(r'register', UserRegisterViewSet, basename='register')

urlpatterns = router.urls

