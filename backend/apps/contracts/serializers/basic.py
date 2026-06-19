from rest_framework import serializers
from apps.contracts.models import CropContract, FarmerContractAllocation

class CropContractSerializer(serializers.ModelSerializer):
  class Meta:
    model = CropContract
    fields = ['id', 'factory', 'crop', 'required_kg', 'allocated_kg', 'base_price_per_kg', 'payment_defer_days', 'quality_grade_expected', 'status', 'delivery_deadline', 'created_at']
    read_only_fields = ['id', 'factory', 'allocated_kg', 'status', 'created_at']

  def validate_required_kg(self, value):
    if value <= 0:
      raise serializers.ValidationError("the need. kg s/h be > than zero.")
    return value

  def validate_base_price_per_kg(self, value):
    if value <= 0:
      raise serializers.ValidationError("the base price per kg s/h be > than zero.")
    return value

  def validate_payment_defer_days(self, value):
    if value < 1 or value > 30:
      raise serializers.ValidationError("the payment defer days s/h be b/w 1 & 30.")
    return value

class FarmerContractAllocationSerializer(serializers.ModelSerializer):
  class Meta:
    model = FarmerContractAllocation
    fields = ['id', 'contract', 'farmer', 'loan', 'committed_kg', 'created_at']
    read_only_fields = ['id', 'created_at']

  def validate_committed_kg(self, value):
    if value <= 0:
      raise serializers.ValidationError("the committed kg s/h be > than zero.")
    return value