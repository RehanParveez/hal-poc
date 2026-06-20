from rest_framework import serializers
from apps.settlements.models import SettlementInvoice

class SettlementInvoiceSerializer(serializers.ModelSerializer):
  farmer_name = serializers.CharField(source = 'loan.farmer.user.full_name', read_only=True)
  farmer_phone = serializers.CharField(source = 'loan.farmer.user.phone', read_only=True)
  crop_name = serializers.CharField(source = 'loan.crop.name', read_only=True)
  crop_code = serializers.CharField(source = 'loan.crop.code', read_only=True)
  batch_kg = serializers.DecimalField(source = 'batch.batch_kg', max_digits=12, decimal_places=2, read_only=True)
  grade_received = serializers.CharField(source = 'batch.grade_received', read_only=True)
  grade_deduction_pct = serializers.DecimalField(source = 'batch.grade_deduction_pct', max_digits=8, decimal_places=2, read_only=True)
  expected_payout = serializers.DecimalField(source = 'batch.expected_payout', max_digits=12, decimal_places=2, read_only=True)
  factory_name = serializers.CharField(source = 'batch.allocation.contract.factory.factory_name', read_only=True)
  payment_defer_days = serializers.IntegerField(source = 'batch.allocation.contract.payment_defer_days', read_only=True)
  agreement_type = serializers.CharField(source = 'tenant_agreement.agreement_type', read_only=True)
  landowner_name = serializers.CharField(source = 'tenant_agreement.parcel.landowner.user.full_name', read_only=True)

  class Meta:
    model = SettlementInvoice
    fields = ['id', 'batch', 'loan', 'tenant_agreement', 'farmer_name', 'farmer_phone', 'crop_name', 'crop_code', 'batch_kg', 'grade_received', 'grade_deduction_pct', 'expected_payout',
      'factory_name', 'payment_defer_days', 'agreement_type', 'landowner_name', 'gross_payout', 'proportional_principal_deduction', 'bank_interest_deduction', 'bank_factoring_commission',
      'platform_transaction_fee', 'theka_payment', 'batai_landowner_share', 'farmer_net_profit', 'insurance_claim_triggered', 'status',
      'bank_advanced_at', 'factory_paid_at', 'created_at']
    read_only_fields = fields