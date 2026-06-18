from django.contrib import admin
from apps.escrow.models import EscrowMilestoneUnlock, EscrowWallet, EscrowTransaction

class EscrowMilestoneUnlockInline(admin.TabularInline):
  model = EscrowMilestoneUnlock
  extra = 0
  fields = ['milestone', 'unlocked_amount', 'unlocked_at', 'is_active']
  readonly_fields = ['milestone', 'unlocked_amount', 'unlocked_at']

@admin.register(EscrowWallet)
class EscrowWalletAdmin(admin.ModelAdmin):
  list_display = ['id', 'get_farmer_name', 'get_district', 'total_funded', 'remaining_balance', 'created_at']
  search_fields = ['id', 'loan__farmer__user__full_name', 'loan__farmer__user__cnic']
  list_filter = ['loan__crop__season', 'created_at']
  inlines = [EscrowMilestoneUnlockInline]
  readonly_fields = ['total_funded', 'insurance_premium_deducted', 'total_spent_on_inputs', 'remaining_balance', 'created_at']

  def get_farmer_name(self, obj):
    return obj.loan.farmer.user.full_name
  get_farmer_name.short_description = 'Farmer'

  def get_district(self, obj):
    return obj.project_district
  get_district.short_description = 'Project District'

@admin.register(EscrowTransaction)
class EscrowTransactionAdmin(admin.ModelAdmin):
  list_display = ['id', 'escrow', 'txn_type', 'amount', 'recipient', 'input_category', 'created_at']
  list_filter = ['txn_type', 'input_category', 'created_at']
  search_fields = ['escrow__id', 'recipient__full_name', 'recipient__cnic']
  
  def has_add_permission(self, request): return False
  def has_change_permission(self, request, obj=None): return False
  def has_delete_permission(self, request, obj=None): return False