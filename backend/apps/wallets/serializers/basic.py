from rest_framework import serializers
from apps.wallets.models import Wallet, WalletTransaction

class WalletSerializer1(serializers.ModelSerializer):
  class Meta:
    model = Wallet
    fields = ['id', 'user', 'wallet_type', 'balance', 'updated_at', 'created_at']
    read_only_fields = ['id', 'user', 'wallet_type', 'balance', 'updated_at', 'created_at']

class WalletTransactionSerializer1(serializers.ModelSerializer):
  class Meta:
    model = WalletTransaction
    fields = ['id', 'wallet', 'amount', 'direction', 'txn_type', 'reference_id', 'note', 'created_at']
    read_only_fields = fields