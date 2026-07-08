from rest_framework import viewsets, status
from apps.contracts.models import CropContract, FarmerContractAllocation
from apps.contracts.serializers.basic import CropContractSerializer
from shared.permissions import FactoryPerm, FarmerPermission
from rest_framework.permissions import IsAuthenticated
from apps.contracts.serializers.detail import CropContractSerializer1, FarmerContractAllocationDetailSerializer
from apps.contracts.services import CropContractService, FarmerContractAllocationService
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.loans.models import LoanApplication
from rest_framework.exceptions import PermissionDenied
from decimal import Decimal

class CropContractViewSet(viewsets.ModelViewSet):
  queryset = CropContract.objects.select_related('factory', 'crop').all()
  serializer_class = CropContractSerializer
  http_method_names = ['get', 'post', 'head', 'options']

  def get_permissions(self):
    if self.action == 'create':
      return [FactoryPerm()]
    return [IsAuthenticated()]

  def get_serializer_class(self):
    if self.action == 'retrieve':
      return CropContractSerializer1
    return CropContractSerializer

  def get_queryset(self):
    queryset = CropContract.objects.select_related('factory', 'crop')
    crop_code = self.request.query_params.get('crop')
    status_filter = self.request.query_params.get('status')
    if crop_code:
      queryset = queryset.filter(crop__code=crop_code.upper())
    if status_filter:
      queryset = queryset.filter(status=status_filter)

    return queryset.order_by('-created_at')

  def create(self, request, *args, **kwargs):
    serializer = CropContractSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    contract = CropContractService.create_contract(factory_profile=request.user.factory_profile, validated_data=serializer.validated_data)
    return Response(CropContractSerializer1(contract).data, status=status.HTTP_201_CREATED)

  @action(detail=True, methods=['post'], permission_classes=[FarmerPermission])
  def allocate(self, request, pk=None):
    loan_id = request.data.get('loan_id')
    committed_kg = request.data.get('committed_kg')
    if not loan_id or not committed_kg:
      return Response({'error': 'the loan_id & committed_kg are need.'}, status=status.HTTP_400_BAD_REQUEST)
    if not hasattr(request.user, 'farmer_profile'):
      return Response({'error': 'User does not have a farmer profile.'}, status=status.HTTP_403_FORBIDDEN)
    committed_kg = Decimal(str(committed_kg))
    try:
      loan = LoanApplication.objects.get(id=loan_id)
    except LoanApplication.DoesNotExist:
      return Response({'error': 'the loan isnt pres.'}, status=status.HTTP_404_NOT_FOUND)
    try:
      allocation = FarmerContractAllocationService.allocate_farmer(contract_id=pk, farmer_profile=request.user.farmer_profile, loan=loan, committed_kg=committed_kg)
    except CropContract.DoesNotExist:
      return Response({'error': 'Contract not found.'}, status=status.HTTP_404_NOT_FOUND)
    except PermissionError as e:
      raise PermissionDenied(str(e))
    except ValueError as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(FarmerContractAllocationDetailSerializer(allocation).data, status=status.HTTP_201_CREATED)

class FarmerContractAllocationViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = FarmerContractAllocation.objects.select_related('farmer__user', 'contract__crop', 'contract__factory', 'loan').all()
  serializer_class = FarmerContractAllocationDetailSerializer

  def get_queryset(self):
    user = self.request.user
    role = user.role
    if role in ('smallholder', 'tenant'):
      return FarmerContractAllocation.objects.filter(farmer=user.farmer_profile).select_related('contract__crop', 'contract__factory', 'loan').order_by('-created_at')
    if role == 'factory':
      return FarmerContractAllocation.objects.filter(contract__factory=user.factory_profile).select_related('farmer__user', 'contract__crop', 'loan').order_by('-created_at')
    return FarmerContractAllocation.objects.none()