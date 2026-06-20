from rest_framework.routers import DefaultRouter
from apps.settlements.views import SettlementInvoiceViewSet
from django.urls import path, include

router = DefaultRouter()
router.register('invoices', SettlementInvoiceViewSet, basename = 'settlement-invoices')

urlpatterns = [
  path('', include(router.urls)),
]