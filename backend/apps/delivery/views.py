from rest_framework import viewsets, status
from apps.delivery.models import BatchDelivery
from decimal import Decimal, InvalidOperation
from apps.delivery.serializers.basic import BatchDeliverySerializer, GradeConfirmationSerializer
from shared.permissions import FarmerPermission, FactoryPerm
from rest_framework.permissions import IsAuthenticated
from apps.delivery.serializers.detail import BatchDeliveryDetailSerializer
from rest_framework.response import Response
from apps.contracts.models import FarmerContractAllocation
from apps.delivery.services import BatchDeliveryService
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action

class BatchDeliveryViewSet(viewsets.ModelViewSet):
  queryset = BatchDelivery.objects.select_related('allocation__farmer__user', 'allocation__contract__crop', 'allocation__contract__factory').all()
  serializer_class = BatchDeliverySerializer
  http_method_names = ['get', 'post', 'patch', 'head', 'options']

  def get_permissions(self):
    if self.action == 'create':
      return [FarmerPermission()]
    if self.action in ('mark_received', 'confirm_grade'):
      return [FactoryPerm()]
    return [IsAuthenticated()]

  def get_serializer_class(self):
    if self.action == 'retrieve':
      return BatchDeliveryDetailSerializer
    if self.action == 'confirm_grade':
      return GradeConfirmationSerializer
    return BatchDeliverySerializer

  def get_queryset(self):
    user = self.request.user
    role = user.role
    if role in ('smallholder', 'tenant'):
      return BatchDelivery.objects.filter(allocation__farmer=user.farmer_profile).select_related('allocation__contract__crop', 'allocation__contract__factory').order_by('-created_at')
    if role == 'factory':
      return BatchDelivery.objects.filter(allocation__contract__factory=user.factory_profile).select_related('allocation__farmer__user',
        'allocation__contract__crop').order_by('-created_at')
    return BatchDelivery.objects.none()
  
  def partial_update(self, request, *args, **kwargs):
    raise PermissionDenied("the direct updates are not allowed. kindly use specific actions.")

  def create(self, request, *args, **kwargs):
    allocation_id = request.data.get('allocation')
    raw_batch_kg = request.data.get('batch_kg')
    try:
      batch_kg = Decimal(str(raw_batch_kg))
    except (InvalidOperation, TypeError):
      return Response({'error': 'batch_kg must be a valid number.'}, status=status.HTTP_400_BAD_REQUEST)

    if not allocation_id or not batch_kg:
      return Response({'error': 'the alloca and batch_kg are need..'}, status=status.HTTP_400_BAD_REQUEST)
    try:
      allocation = FarmerContractAllocation.objects.select_related('contract', 'farmer').get(id=allocation_id)
    except FarmerContractAllocation.DoesNotExist:
      return Response({'error': 'the allocation is not pres.'}, status=status.HTTP_404_NOT_FOUND)
    try:
      batch = BatchDeliveryService.log_delivery(farmer_profile=request.user.farmer_profile, allocation=allocation, batch_kg=batch_kg)
    except PermissionError as e:
      raise PermissionDenied(str(e))
    except ValueError as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(BatchDeliveryDetailSerializer(batch).data, status=status.HTTP_201_CREATED)

  @action(detail=True, methods=['patch'])
  def mark_received(self, request, pk=None):
    try:
      batch = BatchDeliveryService.mark_received(batch_id=pk, factory_profile=request.user.factory_profile)
    except BatchDelivery.DoesNotExist:
      return Response({'error': 'Batch not found.'}, status=status.HTTP_404_NOT_FOUND)
    except PermissionError as e:
      raise PermissionDenied(str(e))
    except ValueError as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'the batch is marked as received.', 'batch': BatchDeliveryDetailSerializer(batch).data})

  @action(detail=True, methods=['patch'])
  def confirm_grade(self, request, pk=None):
    serializer = GradeConfirmationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
      batch = BatchDeliveryService.confirm_grade(batch_id=pk, factory_profile=request.user.factory_profile, grade_received=serializer.validated_data['grade_received'],
        grade_deduction_pct=serializer.validated_data['grade_deduction_pct'], grade_notes=serializer.validated_data.get('grade_notes', ''))
    except BatchDelivery.DoesNotExist:
      return Response({'error': 'the batch is not pres.'}, status=status.HTTP_404_NOT_FOUND)
    except PermissionError as e:
      raise PermissionDenied(str(e))
    except ValueError as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': f"the grade is confirmed. actual payout: PKR {batch.actual_payout}.", 'batch': BatchDeliveryDetailSerializer(batch).data})