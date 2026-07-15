from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.community.views import NumberdarProfileViewSet, FarmerVerificationRequestViewSet

router = DefaultRouter()
router.register('numberdars', NumberdarProfileViewSet, basename = 'numberdars')
router.register('verification-requests', FarmerVerificationRequestViewSet, basename = 'verification-requests')

urlpatterns = [
  path('', include(router.urls)),
]