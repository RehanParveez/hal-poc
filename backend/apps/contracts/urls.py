from rest_framework.routers import DefaultRouter
from apps.contracts.views import CropContractViewSet, FarmerContractAllocationViewSet
from django.urls import path, include

router = DefaultRouter()
router.register('cropcontracts', CropContractViewSet, basename = 'crop-contracts')
router.register('allocations', FarmerContractAllocationViewSet, basename = 'contract-allocations')

urlpatterns = [
  path('', include(router.urls)),
]