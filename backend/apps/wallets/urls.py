from rest_framework.routers import DefaultRouter
from apps.wallets.views import WalletViewSet, WalletTransactionViewSet
from django.urls import path, include

router = DefaultRouter()
router.register('balances', WalletViewSet, basename = 'wallets')
router.register('transactions', WalletTransactionViewSet, basename = 'wallet-transactions')

urlpatterns = [
  path('', include(router.urls)),
]