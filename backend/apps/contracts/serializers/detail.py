from rest_framework import serializers
from apps.contracts.models import CropContract, FarmerContractAllocation
from django.db.models import Sum

class CropContractSerializer1(serializers.ModelSerializer):
  factory_name = serializers.CharField(source = 'factory.factory_name', read_only=True)
  crop_name = serializers.CharField(source = 'crop.name', read_only=True)
  crop_code = serializers.CharField(source = 'crop.code', read_only=True)
  remaining_kg = serializers.ReadOnlyField()
  allocations_count = serializers.SerializerMethodField()

  class Meta:
    model = CropContract
    fields = ['id', 'factory', 'factory_name', 'crop', 'crop_name', 'crop_code', 'required_kg', 'allocated_kg', 'remaining_kg', 'base_price_per_kg',
      'payment_defer_days', 'quality_grade_expected', 'status', 'delivery_deadline', 'allocations_count', 'created_at']
    read_only_fields = fields

  def get_allocations_count(self, obj):
    return obj.allocations.count()

class FarmerContractAllocationDetailSerializer(serializers.ModelSerializer):
  farmer_name = serializers.CharField(source = 'farmer.user.full_name', read_only=True)
  farmer_phone = serializers.CharField(source = 'farmer.user.phone', read_only=True)
  contract_crop_code = serializers.CharField(source = 'contract.crop.code', read_only=True)
  contract_price_per_kg = serializers.DecimalField(source = 'contract.base_price_per_kg', max_digits=10, decimal_places=2, read_only=True)
  factory_name = serializers.CharField(source = 'contract.factory.factory_name', read_only=True)
  loan_status = serializers.CharField(source = 'loan.status', read_only=True)
  delivered_kg = serializers.SerializerMethodField()

  class Meta:
    model = FarmerContractAllocation
    fields = ['id', 'contract', 'farmer', 'farmer_name', 'farmer_phone', 'contract_crop_code', 'contract_price_per_kg', 'factory_name',
      'loan', 'loan_status', 'committed_kg', 'delivered_kg', 'created_at']
    read_only_fields = fields

  def get_delivered_kg(self, obj):
    if not hasattr(obj, 'batches'):
      return 0
    total = obj.batches.aggregate(total=Sum('batch_kg'))['total']
    return total or 0