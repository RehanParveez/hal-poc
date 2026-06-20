from rest_framework import viewsets, status
from apps.settlements.models import SettlementInvoice
from apps.settlements.serializers.basic import SettlementInvoiceSerializer1
from apps.settlements.serializers.detail import SettlementInvoiceSerializer
from rest_framework.decorators import action
from shared.permissions import FactoryPerm
from apps.settlements.services import SettlementService
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

class SettlementInvoiceViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = SettlementInvoice.objects.select_related('loan__farmer__user', 'loan__crop', 'batch', 'tenant_agreement__parcel__landowner__user').all()
  serializer_class = SettlementInvoiceSerializer1

  def get_serializer_class(self):
    if self.action == 'retrieve':
      return SettlementInvoiceSerializer
    return SettlementInvoiceSerializer1

  def get_queryset(self):
    user = self.request.user
    role = user.role
    if role in ('smallholder', 'tenant'):
      queryset = SettlementInvoice.objects.filter(loan__farmer=user.farmer_profile)
    elif role == 'bank':
      queryset = SettlementInvoice.objects.filter(loan__bank=user.bank_profile)
    elif role == 'factory':
      queryset = SettlementInvoice.objects.filter(batch__allocation__contract__factory=user.factory_profile)
    elif role == 'landowner':
      queryset = SettlementInvoice.objects.filter(tenant_agreement__parcel__landowner=user.landowner_profile)
    else:
      return SettlementInvoice.objects.none()

    queryset = queryset.select_related('loan__farmer__user', 'loan__crop', 'batch', 'tenant_agreement__parcel__landowner__user')
    loan_id = self.request.query_params.get('loan')
    status_filter = self.request.query_params.get('status')
    if loan_id:
      queryset = queryset.filter(loan_id=loan_id)
    if status_filter:
      queryset = queryset.filter(status=status_filter)
    return queryset.order_by('-created_at')
  
  @action(detail=True, methods=['post'], permission_classes=[FactoryPerm])
  def factory_settle(self, request, pk=None):
   try:
    invoice = SettlementService.confirm_factory_settlement(invoice_id=pk, factory_profile=request.user.factory_profile)
   except SettlementInvoice.DoesNotExist:
    return Response({'error': 'Invoice not found.'}, status=status.HTTP_404_NOT_FOUND)
   except PermissionError as e:
    raise PermissionDenied(str(e))
   except ValueError as e:
    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
   return Response({'message': 'Factory settlement confirmed. Bank wallet credited.', 'invoice': SettlementInvoiceSerializer(invoice).data})