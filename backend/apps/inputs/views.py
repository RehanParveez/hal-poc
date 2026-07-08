from rest_framework import viewsets, status
from shared.permissions import FarmerPermission, BankManagerPerm, ShopkeeperPerm, AdminPerm
from apps.inputs.models import InputSupplyRequest
from apps.inputs.serializers import InputSupplyRequestSerializer1, InputSupplyRequestSerializer, InputPaymentCreateSerializer
from rest_framework.response import Response
from apps.inputs.services import process_input_request

class InputSupplyRequestViewSet(viewsets.ModelViewSet):
  http_method_names = ['get', 'post', 'head', 'options']
  
  def get_permissions(self):
    if self.action == 'create':
      return [FarmerPermission()]
    comb = BankManagerPerm | ShopkeeperPerm | FarmerPermission | AdminPerm
    return [comb()]

  def get_queryset(self):
    user = self.request.user
    base_qs = InputSupplyRequest.objects.select_related('escrow__loan__farmer__user', 'escrow__loan__crop', 'shopkeeper__user')
    if user.role in ('smallholder', 'tenant'):
      return base_qs.filter(escrow__loan__farmer__user=user)
    if user.role == 'shopkeeper':
      return base_qs.filter(shopkeeper__user=user)
    if user.role in ('bank'):
      return base_qs.filter(escrow__loan__bank=user.bank_profile)
    if user.role == 'admin':
      return base_qs.all()
    return InputSupplyRequest.objects.none()

  def get_serializer_class(self):
    if self.action == 'retrieve':
      return InputSupplyRequestSerializer1
    return InputSupplyRequestSerializer

  def list(self, request, *args, **kwargs):
    category = request.query_params.get('input_category')
    status_filter = request.query_params.get('status')
    qs = self.get_queryset()
    if category:
      qs = qs.filter(input_category=category)
    if status_filter:
      qs = qs.filter(status=status_filter)
    serializer = InputSupplyRequestSerializer(qs, many=True)
    return Response(serializer.data)

  def retrieve(self, request, *args, **kwargs):
    instance = self.get_object()
    if request.user.role in ('smallholder', 'tenant'):
      if instance.escrow.loan.farmer.user != request.user:
        return Response({'error': 'You do not have access to this request.'}, status=status.HTTP_403_FORBIDDEN)
    if request.user.role == 'shopkeeper':
      if instance.shopkeeper.user != request.user:
        return Response({'error': 'You do not have access to this request.'}, status=status.HTTP_403_FORBIDDEN)
    serializer = InputSupplyRequestSerializer1(instance)
    return Response(serializer.data)

  def create(self, request, *args, **kwargs):
    serializer = InputPaymentCreateSerializer(data=request.data)
    if not serializer.is_valid():
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    from apps.escrow.models import EscrowWallet
    try:
      escrow = EscrowWallet.objects.select_related('loan__farmer__user').get(id=data['escrow_id'])
    except EscrowWallet.DoesNotExist:
      return Response({'error': 'Escrow wallet not found.'}, status=status.HTTP_404_NOT_FOUND)
    if escrow.loan.farmer.user != request.user:
      return Response({'error': 'This escrow does not belong to your account.'}, status=status.HTTP_403_FORBIDDEN)
    from apps.accounts.models import ShopkeeperProfile
    try:
      shopkeeper_profile = ShopkeeperProfile.objects.select_related('user').get(user_id=data['shopkeeper_id'])
    except ShopkeeperProfile.DoesNotExist:
      return Response({'error': 'Shopkeeper not found. Ensure they are registered on FasalPay.'}, status=status.HTTP_404_NOT_FOUND)
  
    supply_request = process_input_request(escrow_id=data['escrow_id'], shopkeeper_profile=shopkeeper_profile, input_category=data['input_category'], amount=data['amount'], description=data.get('item_description', ''))
    escrow.refresh_from_db()
    return Response({'message': 'Payment successful. Shopkeeper wallet credited instantly.', 'supply_request': InputSupplyRequestSerializer1(supply_request).data, 'escrow_remaining_balance': str(escrow.remaining_balance)}, status=status.HTTP_201_CREATED)

class ShopkeeperPaymentHistoryViewSet(viewsets.ReadOnlyModelViewSet):
  http_method_names = ['get', 'head', 'options']
  
  def get_permissions(self):
    return [ShopkeeperPerm()]

  def get_queryset(self):
    return InputSupplyRequest.objects.select_related('escrow__loan__farmer__user', 'escrow__loan__crop', 'shopkeeper__user').filter(shopkeeper__user=self.request.user,
      status='paid')
    
  def get_serializer_class(self):
    if self.action == 'retrieve':
      return InputSupplyRequestSerializer1
    return InputSupplyRequestSerializer

  def list(self, request, *args, **kwargs):
    category = request.query_params.get('input_category')
    qs = self.get_queryset()
    if category:
      qs = qs.filter(input_category=category)
    serializer = InputSupplyRequestSerializer(qs, many=True)
    return Response(serializer.data)