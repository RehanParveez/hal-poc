from rest_framework import serializers
from apps.wallets.models import Wallet, WalletTransaction
from apps.wallets.serializers.basic import WalletTransactionSerializer1

class WalletSerializer(serializers.ModelSerializer):
  user_name = serializers.CharField(source = 'user.full_name', read_only=True)
  user_phone = serializers.CharField(source = 'user.phone', read_only=True)
  user_role = serializers.CharField(source = 'user.role', read_only=True)
  recent_transactions = serializers.SerializerMethodField()

  class Meta:
    model = Wallet
    fields = ['id', 'user', 'user_name', 'user_phone', 'user_role', 'wallet_type', 'balance', 'recent_transactions', 'updated_at', 'created_at']
    read_only_fields = fields

  def get_recent_transactions(self, obj):
    recent = obj.transactions.order_by('-created_at')[:5]
    return WalletTransactionSerializer1(recent, many=True).data

class WalletTransactionSerializer(serializers.ModelSerializer):
  wallet_owner_name = serializers.CharField(source = 'wallet.user.full_name', read_only=True)
  wallet_type = serializers.CharField(source = 'wallet.wallet_type', read_only=True)

  class Meta:
    model = WalletTransaction
    fields = ['id', 'wallet', 'wallet_owner_name', 'wallet_type', 'amount', 'direction', 'txn_type', 'reference_id', 'note', 'created_at']
    read_only_fields = fields