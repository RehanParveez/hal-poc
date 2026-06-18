from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.escrow.views import EscrowWalletViewSet

router = DefaultRouter()
router.register('wallets', EscrowWalletViewSet, basename = 'escrow-wallet')

urlpatterns = [
  path('', include(router.urls)),
]