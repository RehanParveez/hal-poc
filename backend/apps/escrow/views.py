from rest_framework import viewsets, status
from apps.escrow.models import EscrowWallet
from apps.escrow.serializers.detail import EscrowWalletSerializer, EscrowTransactionSerializer
from shared.permissions import FarmerPermission, BankManagerPerm
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.escrow.serializers.basic import AFOCapCheckSerializer
from apps.crops.models import CropInputCap
from apps.escrow.services import EscrowCreationService
from decimal import Decimal
from django.db.models import Sum

class EscrowWalletViewSet(viewsets.GenericViewSet):
  queryset = EscrowWallet.objects.all()
  serializer_class = EscrowWalletSerializer
  permission_classes = [FarmerPermission | BankManagerPerm]

  def get_object(self):
    obj = super().get_object()
    user = self.request.user
    if user.role in ('smallholder', 'tenant'):
      if obj.loan.farmer.user != user:
        self.permission_denied(self.request)
    if user.role == 'bank':
      if obj.loan.bank.user != user:
        self.permission_denied(self.request)
    return obj

  @action(detail=True, methods=['get'])
  def balance(self, request, pk=None):
    escrow = self.get_object()
    return Response(self.get_serializer(escrow).data)

  @action(detail=True, methods=['get'])
  def transactions(self, request, pk=None):
    escrow = self.get_object()
    txn_type = request.query_params.get('txn_type')
    qs = escrow.transactions.select_related('recipient').order_by('-created_at')
    if txn_type:
      qs = qs.filter(txn_type=txn_type)
    serializer = EscrowTransactionSerializer(qs, many=True)
    return Response({'escrow_id': str(escrow.id), 'count': qs.count(), 'transactions': serializer.data})

  @action(detail=True, methods=['get'])
  def afo_caps(self, request, pk=None):
    escrow = self.get_object()
    active_unlock = escrow.unlocks.filter(is_active=True).select_related('milestone').first()
    currently_allowed = active_unlock.milestone.allowed_input_categories if active_unlock else []
    caps = CropInputCap.objects.filter(crop=escrow.loan.crop, district=escrow.loan.farmer.user.district, valid_season=escrow.loan.crop.season)
    
    result = []
    for cap in caps:
      total_cap = (cap.max_cost_per_acre * escrow.loan.acres_applied_for).quantize(Decimal('0.01'))
      already_spent = escrow.transactions.filter(txn_type='input', input_category=cap.input_category).aggregate(total=Sum('amount'))['total'] or Decimal('0')
      result.append({'category': cap.input_category, 'cap_per_acre': cap.max_cost_per_acre, 'total_cap': total_cap,
        'already_spent': already_spent, 'remaining': max(Decimal('0'), total_cap - already_spent),
        'is_allowed_now': cap.input_category in currently_allowed})
      
    return Response({'escrow_id': str(escrow.id), 'farmer': escrow.loan.farmer.user.full_name,
      'active_phase': active_unlock.milestone.phase_name if active_unlock else None, 'currently_allowed': currently_allowed,
      'caps': AFOCapCheckSerializer(result, many=True).data})

  @action(detail=True, methods=['patch'], permission_classes=[BankManagerPerm])
  def unlock_next_phase(self, request, pk=None):
    escrow = self.get_object()
    try:
      next_milestone = EscrowCreationService.unlock_next_phase(escrow.id)
      escrow.refresh_from_db()
      return Response({'message': f"Phase {next_milestone.phase_number} active.", 'new_phase_number': next_milestone.phase_number,
        'escrow': EscrowWalletSerializer(escrow).data})
    except ValueError as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)