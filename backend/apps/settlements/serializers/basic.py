from rest_framework import serializers
from apps.settlements.models import SettlementInvoice

class SettlementInvoiceSerializer1(serializers.ModelSerializer):
  class Meta:
    model = SettlementInvoice
    fields = ['id', 'batch', 'loan', 'tenant_agreement', 'gross_payout', 'proportional_principal_deduction', 'bank_interest_deduction', 'bank_factoring_commission',
      'platform_transaction_fee', 'theka_payment', 'batai_landowner_share', 'farmer_net_profit', 'insurance_claim_triggered', 'status',
      'bank_advanced_at', 'factory_paid_at', 'created_at']
    read_only_fields = fields