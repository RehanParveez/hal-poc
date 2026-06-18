from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.crops.views import CropTypeViewSet, CropInputCapViewSet, CropLifecycleMilestoneViewSet

router = DefaultRouter()
router.register('types', CropTypeViewSet, basename = 'crop-types')
router.register('inputcaps', CropInputCapViewSet, basename = 'crop-input-caps')
router.register('milestones', CropLifecycleMilestoneViewSet, basename = 'crop-milestones')

urlpatterns = [
  path('', include(router.urls)),
]