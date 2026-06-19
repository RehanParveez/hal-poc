from rest_framework.routers import DefaultRouter
from apps.inputs.views import InputSupplyRequestViewSet, ShopkeeperPaymentHistoryViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'requests', InputSupplyRequestViewSet, basename = 'input-request')
router.register(r'shopkeeper-history', ShopkeeperPaymentHistoryViewSet, basename = 'shopkeeper-history')

urlpatterns = [
  path('', include(router.urls)),
]