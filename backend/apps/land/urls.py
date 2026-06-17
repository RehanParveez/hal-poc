from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.land.views import LandViewSet, TenantAgreementViewSet

router = DefaultRouter()
router.register('lands', LandViewSet, basename = 'lands')
router.register('agreements', TenantAgreementViewSet, basename = 'agreements')

urlpatterns = [
  path('', include(router.urls)),
]