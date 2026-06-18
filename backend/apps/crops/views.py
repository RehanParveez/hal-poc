from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from shared.permissions import AFOOfficerPerm
from apps.crops.models import CropType, CropInputCap, CropLifecycleMilestone
from apps.crops.serializers import CropTypeSerializer, CropInputCapSerializer, CropLifecycleMilestoneSerializer
from apps.crops.services import CropTypeService, CropInputCapService, CropLifecycleMilestoneService

class CropTypeViewSet(viewsets.ModelViewSet):
  queryset = CropType.objects.filter(is_active=True).order_by('name')
  serializer_class = CropTypeSerializer

  def get_permissions(self):
    if self.action in ('create', 'update', 'partial_update', 'destroy'):
      return [AFOOfficerPerm()]
    return [IsAuthenticated()]

  def get_queryset(self):
    queryset = CropType.objects.filter(is_active=True)
    season = self.request.query_params.get('season')
    if season:
      queryset = queryset.filter(season=season)
    return queryset.order_by('name')

  def perform_create(self, serializer):
    CropTypeService.create_crop(serializer.validated_data)

  def create(self, request, *args, **kwargs):
    serializer = CropTypeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    crop = CropTypeService.create_crop(serializer.validated_data)
    return Response(CropTypeSerializer(crop).data, status=status.HTTP_201_CREATED)

  def partial_update(self, request, *args, **kwargs):
    crop = self.get_object()
    serializer = CropTypeSerializer(crop, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    updated = CropTypeService.update_crop(crop, serializer.validated_data)
    return Response(CropTypeSerializer(updated).data)

class CropInputCapViewSet(viewsets.ModelViewSet):
  queryset = CropInputCap.objects.select_related('crop').filter(is_active=True)
  serializer_class = CropInputCapSerializer

  def get_permissions(self):
    if self.action in ('create', 'update', 'partial_update', 'destroy'):
      return [AFOOfficerPerm()]
    return [IsAuthenticated()]

  def get_queryset(self):
    queryset = CropInputCap.objects.select_related('crop').filter(is_active=True)
    crop_code = self.request.query_params.get('crop')
    district = self.request.query_params.get('district')
    season = self.request.query_params.get('season')
    category = self.request.query_params.get('category')
    if crop_code:
      queryset = queryset.filter(crop__code=crop_code.upper())
    if district:
      queryset = queryset.filter(district=district)
    if season:
      queryset = queryset.filter(valid_season=season)
    if category:
      queryset = queryset.filter(input_category=category)
    return queryset.order_by('crop__code', 'district', 'input_category')

  def create(self, request, *args, **kwargs):
    serializer = CropInputCapSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    cap, created = CropInputCapService.set_cap(serializer.validated_data)
    response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return Response(CropInputCapSerializer(cap).data, status=response_status)

class CropLifecycleMilestoneViewSet(viewsets.ModelViewSet):
  queryset = CropLifecycleMilestone.objects.select_related('crop').filter(is_active=True)
  serializer_class = CropLifecycleMilestoneSerializer

  def get_permissions(self):
    if self.action in ('create', 'update', 'partial_update', 'destroy'):
      return [AFOOfficerPerm()]
    return [IsAuthenticated()]

  def get_queryset(self):
    queryset = CropLifecycleMilestone.objects.select_related('crop').filter(is_active=True)
    crop_code = self.request.query_params.get('crop')
    if crop_code:
      queryset = queryset.filter(crop__code=crop_code.upper())
    return queryset.order_by('crop__code', 'phase_number')

  def create(self, request, *args, **kwargs):
    serializer = CropLifecycleMilestoneSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    milestone, created = CropLifecycleMilestoneService.set_milestone(serializer.validated_data)
    response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return Response(CropLifecycleMilestoneSerializer(milestone).data, status=response_status)