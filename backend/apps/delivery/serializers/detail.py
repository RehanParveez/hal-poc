from rest_framework import serializers
from apps.delivery.models import BatchDelivery

class BatchDeliveryDetailSerializer(serializers.ModelSerializer):
  farmer_name = serializers.CharField(source = 'allocation.farmer.user.full_name', read_only=True)
  farmer_phone = serializers.CharField(source = 'allocation.farmer.user.phone', read_only=True)
  contract_crop_code = serializers.CharField(source = 'allocation.contract.crop.code', read_only=True)
  contract_price_per_kg = serializers.DecimalField(source = 'allocation.contract.base_price_per_kg', max_digits=10, decimal_places=2, read_only=True)
  factory_name = serializers.CharField(source = 'allocation.contract.factory.factory_name', read_only=True)
  payment_defer_days = serializers.IntegerField(source = 'allocation.contract.payment_defer_days', read_only=True)
  loan_id = serializers.UUIDField(source = 'allocation.loan.id', read_only=True)

  class Meta:
    model = BatchDelivery
    fields = ['id', 'allocation', 'farmer_name', 'farmer_phone', 'contract_crop_code', 'contract_price_per_kg', 'factory_name', 'payment_defer_days', 'loan_id',
      'batch_kg', 'expected_payout', 'actual_payout', 'grade_received', 'grade_deduction_pct', 'grade_notes', 'status', 'delivered_at', 'grade_confirmed_at', 'created_at']
    read_only_fields = fields