from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from shared.permissions import FarmerPermission, NumberdarPerm, AdminPerm
from apps.community.models import NumberdarProfile, FarmerVerificationRequest
from apps.community.serializers import NumberdarProfileSerializer, FarmerVerificationRequestSerializer, VerificationRejectSerializer
from apps.community.services import NumberdarVerificationService

class NumberdarProfileViewSet(viewsets.ReadOnlyModelViewSet):
  serializer_class = NumberdarProfileSerializer
  http_method_names = ['get', 'head', 'options']

  def get_permissions(self):
    return [(FarmerPermission | AdminPerm)()]

  def get_queryset(self):
    queryset = NumberdarProfile.objects.select_related('user').filter(is_active=True)
    district = self.request.query_params.get('district')
    if district:
      queryset = queryset.filter(jurisdiction_district=district)
    return queryset.order_by('jurisdiction_district')

class FarmerVerificationRequestViewSet(viewsets.ModelViewSet):
  serializer_class = FarmerVerificationRequestSerializer
  http_method_names = ['get', 'post', 'patch', 'head', 'options']

  def get_permissions(self):
    if self.action == 'create':
      return [FarmerPermission()]
    if self.action in ('approve', 'reject'):
      return [NumberdarPerm()]
    return [(FarmerPermission | NumberdarPerm | AdminPerm)()]

  def get_queryset(self):
    user = self.request.user
    base_qs = FarmerVerificationRequest.objects.select_related('farmer__user', 'numberdar__user')
    if user.role in ('smallholder', 'tenant'):
      return base_qs.filter(farmer=user.farmer_profile).order_by('-created_at')
    if user.role == 'numberdar':
      qs = base_qs.filter(numberdar=user.numberdar_profile)
      status_filter = self.request.query_params.get('status')
      if status_filter:
        qs = qs.filter(status=status_filter)
      return qs.order_by('-created_at')
    if user.role == 'admin':
      return base_qs.all().order_by('-created_at')
    return FarmerVerificationRequest.objects.none()

  def create(self, request, *args, **kwargs):
    numberdar_id = request.data.get('numberdar_id')
    if not numberdar_id:
      return Response({'error': 'numberdar_id is need.'}, status=status.HTTP_400_BAD_REQUEST)
    req = NumberdarVerificationService.submit_verification_request(
      farmer_profile=request.user.farmer_profile, numberdar_id=numberdar_id)
    return Response(FarmerVerificationRequestSerializer(req).data, status=status.HTTP_201_CREATED)

  @action(detail=True, methods=['patch'])
  def approve(self, request, pk=None):
    try:
      req = NumberdarVerificationService.approve_farmer(request_id=pk, numberdar_user=request.user)
    except FarmerVerificationRequest.DoesNotExist:
      return Response({'error': 'verification request is not pres.'}, status=status.HTTP_404_NOT_FOUND)
    except PermissionError as e:
      raise PermissionDenied(str(e))
    except ValueError as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': f'{req.farmer.user.full_name} has been verified and can now apply for a loan.',
      'request': FarmerVerificationRequestSerializer(req).data})

  @action(detail=True, methods=['patch'])
  def reject(self, request, pk=None):
    serializer = VerificationRejectSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
      req = NumberdarVerificationService.reject_farmer(request_id=pk, numberdar_user=request.user, notes=serializer.validated_data['notes'])
    except FarmerVerificationRequest.DoesNotExist:
      return Response({'error': 'verification request is not pres.'}, status=status.HTTP_404_NOT_FOUND)
    except PermissionError as e:
      raise PermissionDenied(str(e))
    except ValueError as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'Request rejected.', 'request': FarmerVerificationRequestSerializer(req).data})