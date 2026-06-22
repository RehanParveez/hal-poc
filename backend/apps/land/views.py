from rest_framework import viewsets, status
from shared.permissions import TenantFarmerPerm, LandownerPerm, BankManagerPerm
from apps.land.serializers.basic import LandSerializer, TenantAgreementSerializer
from apps.land.models import Land, TenantAgreement
from rest_framework.exceptions import PermissionDenied
from apps.land.services import LandService, TenantAgreementService
from apps.land.serializers.detail import TenantAgreementDetailSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class LandViewSet(viewsets.ModelViewSet):
  def get_permissions(self):
    if self.action == 'create': return [LandownerPerm()]
    if self.action in ('list', 'retrieve'):
      comb = LandownerPerm | BankManagerPerm | TenantFarmerPerm
      return [comb()]
    return [LandownerPerm()]

  def get_serializer_class(self):
    return LandSerializer

  def get_queryset(self):
    if self.request.user.role == 'landowner':
      return Land.objects.filter(landowner=self.request.user.landowner_profile).order_by('-created_at')
    district = self.request.query_params.get('district')
    queryset = Land.objects.all()
    if district: queryset = queryset.filter(district=district)
    return queryset.order_by('-created_at')

  def create(self, request, *args, **kwargs):
    if request.user.role != 'landowner': raise PermissionDenied("Only landowners can register land parcels.")
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    parcel = LandService.create_parcel(landowner_profile=request.user.landowner_profile, validated_data=serializer.validated_data)
    return Response(self.get_serializer(parcel).data, status=status.HTTP_201_CREATED)

class TenantAgreementViewSet(viewsets.ModelViewSet):
  def get_permissions(self):
    if self.action == 'create': return [TenantFarmerPerm()]
    if self.action in ('approve', 'reject'): return [LandownerPerm()]
    return []

  def get_serializer_class(self):
    if self.action in ('list', 'retrieve'): return TenantAgreementDetailSerializer
    return TenantAgreementSerializer

  def get_queryset(self):
    role = self.request.user.role
    if role not in ('tenant', 'landowner', 'bank'): raise PermissionDenied('You dont have the access to this res.')
    if role == 'tenant':
      return TenantAgreement.objects.filter(tenant=self.request.user.farmer_profile).select_related('parcel', 'parcel__landowner__user').order_by('-created_at')
    if role == 'landowner':
      return TenantAgreement.objects.filter(parcel__landowner=self.request.user.landowner_profile).select_related('tenant__user', 'parcel').order_by('-created_at')
    if role == 'bank':
      queryset = TenantAgreement.objects.filter(status='active').select_related('tenant__user', 'parcel', 'parcel__landowner__user')
      district = self.request.query_params.get('district')
      if district: queryset = queryset.filter(parcel__district=district)
      return queryset.order_by('-created_at')

  def create(self, request, *args, **kwargs):
    serializer = TenantAgreementSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    agreement = serializer.save()
    agreement_fresh = TenantAgreement.objects.select_related('tenant__user', 'parcel', 'parcel__landowner__user').get(id=agreement.id)
    return Response(TenantAgreementDetailSerializer(agreement_fresh).data, status=status.HTTP_201_CREATED)

  @action(detail=True, methods=['patch'])
  def approve(self, request, pk=None):
    try:
      agreement = TenantAgreementService.approve_agreement(agreement_id=pk, landowner_profile=request.user.landowner_profile)
    except TenantAgreement.DoesNotExist:
      return Response({'error': 'the agreemt is not pres.'}, status=status.HTTP_404_NOT_FOUND)
    except (PermissionError, ValueError) as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    agreement_fresh = TenantAgreement.objects.select_related('tenant__user', 'parcel', 'parcel__landowner__user').get(id=agreement.id)
    return Response({'message': f'the agreem is appro. {agreement_fresh.tenant.user.full_name} can now apply for a loan.',
      'agreement': TenantAgreementDetailSerializer(agreement_fresh).data})

  @action(detail=True, methods=['patch'])
  def reject(self, request, pk=None):
    reason = request.data.get('reason', '')
    try:
      agreement = TenantAgreementService.reject_agreement(agreement_id=pk, landowner_profile=request.user.landowner_profile, reason=reason)
    except TenantAgreement.DoesNotExist:
      return Response({'error': 'the agreem is not pres.'}, status=status.HTTP_404_NOT_FOUND)
    except (PermissionError, ValueError) as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'the agree is rej.', 'agreement_id': str(agreement.id), 'status': agreement.status})