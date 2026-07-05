from rest_framework import viewsets, status
from apps.wallets.models import Wallet, WalletTransaction
from apps.wallets.serializers.basic import WalletSerializer1, WalletTransactionSerializer1
from rest_framework.permissions import IsAuthenticated
from apps.wallets.serializers.detail import WalletSerializer, WalletTransactionSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class WalletViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = Wallet.objects.select_related('user').all()
  serializer_class = WalletSerializer1
  permission_classes = [IsAuthenticated]
  
  def get_queryset(self):
    if self.request.user.role == 'admin':
      return Wallet.objects.select_related('user').all().order_by('-created_at')
    return Wallet.objects.select_related('user').filter(user=self.request.user).order_by('-created_at')

  def get_serializer_class(self):
    if self.action == 'retrieve':
      return WalletSerializer
    return WalletSerializer1

  @action(detail=False, methods=['get'])
  def my_balance(self, request):
   try:
    wallet = Wallet.objects.select_related('user').get(user=request.user)
   except Wallet.DoesNotExist:
    return Response({'error': 'You do not have a wallet yet.'}, status=status.HTTP_404_NOT_FOUND)
   return Response(WalletSerializer(wallet).data)

class WalletTransactionViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = WalletTransaction.objects.select_related('wallet__user').all()
  serializer_class = WalletTransactionSerializer
  permission_classes = [IsAuthenticated]
  
  def get_serializer_class(self):
    if self.action == 'retrieve':
      return WalletTransactionSerializer
    return WalletTransactionSerializer1

  def get_queryset(self):
    queryset = WalletTransaction.objects.filter(wallet__user=self.request.user).select_related('wallet__user')
    txn_type = self.request.query_params.get('txn_type')
    direction = self.request.query_params.get('direction')
    if txn_type:
      queryset = queryset.filter(txn_type=txn_type)
    if direction:
      queryset = queryset.filter(direction=direction)

    return queryset.order_by('-created_at')