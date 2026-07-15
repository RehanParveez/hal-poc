from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.credit.views import CreditCheckViewSet

router = DefaultRouter()
router.register('checks', CreditCheckViewSet, basename = 'credit-checks')

urlpatterns = [
  path('', include(router.urls))
]
