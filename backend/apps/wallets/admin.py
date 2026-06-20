from django.contrib import admin
from apps.wallets.models import Wallet, WalletTransaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
  list_display = ['id', 'user', 'wallet_type', 'balance', 'is_active', 'updated_at']
  search_fields = ['user__full_name', 'user__phone']
  list_filter = ['wallet_type', 'is_active']

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
  list_display = ['id', 'wallet', 'amount', 'direction', 'txn_type', 'reference_id', 'created_at']
  search_fields = ['wallet__user__full_name']
  list_filter = ['txn_type', 'direction']