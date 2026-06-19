from rest_framework import serializers
from apps.inputs.models import InputSupplyRequest
from decimal import Decimal
 
class InputSupplyRequestSerializer(serializers.ModelSerializer):
  farmer_name = serializers.CharField(source = 'escrow.loan.farmer.user.full_name', read_only=True)
  shopkeeper_name = serializers.CharField(source = 'shopkeeper.shop_name', read_only=True)
  escrow_id = serializers.UUIDField(source = 'escrow.id', read_only=True)

  class Meta:
    model = InputSupplyRequest
    fields = ['id', 'escrow_id', 'farmer_name', 'shopkeeper_name', 'input_category', 'requested_amount', 'status', 'created_at']
 
class InputSupplyRequestSerializer1(serializers.ModelSerializer):
  farmer_name = serializers.CharField(source = 'escrow.loan.farmer.user.full_name', read_only=True)
  farmer_district = serializers.CharField(source = 'escrow.loan.farmer.user.district', read_only=True)
  shopkeeper_name = serializers.CharField(source = 'shopkeeper.shop_name', read_only=True)
  shopkeeper_phone = serializers.CharField(source = 'shopkeeper.user.phone', read_only=True)
  escrow_id = serializers.UUIDField(source = 'escrow.id', read_only=True)
  escrow_remaining_balance = serializers.DecimalField(source = 'escrow.remaining_balance', max_digits=14, decimal_places=2, read_only=True)
  crop_name = serializers.CharField(source = 'escrow.loan.crop.name', read_only=True)
  loan_id = serializers.UUIDField(source = 'escrow.loan.id', read_only=True)
 
  class Meta:
    model = InputSupplyRequest
    fields = ['id', 'loan_id', 'escrow_id', 'escrow_remaining_balance', 'farmer_name', 'farmer_district', 'shopkeeper_name', 'shopkeeper_phone',
      'crop_name', 'input_category', 'item_description', 'requested_amount', 'afo_cap_at_time', 'status', 'created_at', 'updated_at']
 
class InputPaymentCreateSerializer(serializers.Serializer):
  INPUT_CATEGORIES = ['seed', 'fertilizer', 'pesticide', 'irrigation', 'labour']
  escrow_id = serializers.UUIDField()
  shopkeeper_id = serializers.UUIDField()
  input_category = serializers.ChoiceField(choices=INPUT_CATEGORIES)
  amount = serializers.DecimalField(max_digits=16, decimal_places=2, min_value=Decimal('1.00')) 
  item_description = serializers.CharField(max_length=300, required=False, allow_blank=True, default='')

  def validate_amount(self, value):
    if value <= 0:
      raise serializers.ValidationError("the amount s/h be > than zero.")
    return value