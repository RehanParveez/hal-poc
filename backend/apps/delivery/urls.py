from rest_framework.routers import DefaultRouter
from apps.delivery.views import BatchDeliveryViewSet
from django.urls import path, include

router = DefaultRouter()
router.register('batches', BatchDeliveryViewSet, basename = 'batch-deliveries')

urlpatterns = [
  path('', include(router.urls)),
]