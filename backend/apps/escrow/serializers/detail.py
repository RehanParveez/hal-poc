from rest_framework import serializers
from apps.escrow.models import EscrowWallet, EscrowTransaction
from apps.escrow.serializers.basic import EscrowMilestoneUnlockSerializer
from decimal import Decimal

class EscrowWalletSerializer(serializers.ModelSerializer):
  loan_id = serializers.UUIDField(source = 'loan.id', read_only=True)
  loan_crop_code = serializers.CharField(source = 'loan.crop.code', read_only=True)
  loan_crop_name = serializers.CharField(source = 'loan.crop.name', read_only=True)
  loan_acres = serializers.DecimalField(source = 'loan.acres_applied_for', max_digits=12, decimal_places=2, read_only=True)
  loan_season = serializers.CharField(source = 'loan.crop.season', read_only=True)
  farmer_name = serializers.CharField(source = 'loan.farmer.user.full_name', read_only=True)
  project_district = serializers.CharField()
  active_phase = serializers.SerializerMethodField()
  all_phases = serializers.SerializerMethodField()
  spend_percentage = serializers.SerializerMethodField()

  class Meta:
    model = EscrowWallet
    fields = ['id', 'loan_id', 'loan_crop_code', 'loan_crop_name', 'loan_acres', 'loan_season', 'farmer_name', 'project_district', 'total_funded',
      'insurance_premium_deducted', 'total_spent_on_inputs', 'remaining_balance', 'spend_percentage', 'active_phase', 'all_phases', 'created_at']

  def get_active_phase(self, obj):
    unlock = obj.active_unlock
    return EscrowMilestoneUnlockSerializer(unlock).data if unlock else None

  def get_all_phases(self, obj):
    unlocks = obj.unlocks.select_related('milestone').order_by('milestone__phase_number')
    return EscrowMilestoneUnlockSerializer(unlocks, many=True).data

  def get_spend_percentage(self, obj):
    if not obj.total_funded:
      return 0
    pct = (obj.total_spent_on_inputs / obj.total_funded) * Decimal('100')
    return round(float(pct), 1)

class EscrowTransactionSerializer(serializers.ModelSerializer):
  recipient_name = serializers.CharField(source = 'recipient.full_name', read_only=True)
  recipient_role = serializers.CharField(source = 'recipient.role', read_only=True)
  shop_name = serializers.SerializerMethodField()

  class Meta:
    model = EscrowTransaction
    fields = ['id', 'txn_type', 'amount', 'input_category', 'afo_cap_snapshot', 'recipient_name', 'recipient_role', 'shop_name', 'created_at']

  def get_shop_name(self, obj):
    if obj.txn_type == 'input_payment' and hasattr(obj.recipient, 'shopkeeper_profile'):
      return obj.recipient.shopkeeper_profile.shop_name
    return None