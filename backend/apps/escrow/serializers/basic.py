from rest_framework import serializers
from apps.escrow.models import EscrowMilestoneUnlock
from decimal import Decimal

class EscrowMilestoneUnlockSerializer(serializers.ModelSerializer):
  phase_number = serializers.IntegerField(source = 'milestone.phase_number', read_only=True)
  phase_name = serializers.CharField(source = 'milestone.phase_name', read_only=True)
  day_offset = serializers.IntegerField(source = 'milestone.day_offset', read_only=True)
  allowed_categories = serializers.ListField(source = 'milestone.allowed_input_categories', read_only=True)

  class Meta:
    model = EscrowMilestoneUnlock
    fields = ['id', 'phase_number', 'phase_name', 'day_offset', 'allowed_categories', 'unlocked_amount', 'unlocked_at', 'is_active']

class InputPaymentRequestSerializer(serializers.Serializer):
  INPUT_CATEGORIES = ['seed', 'fertilizer', 'pesticide', 'irrigation', 'labour']
  shopkeeper_user_id = serializers.UUIDField()
  input_category = serializers.ChoiceField(choices=INPUT_CATEGORIES)
  amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('1.00'))
  item_description = serializers.CharField(max_length=300, required=False, allow_blank=True, default='')

  def validate_amount(self, value):
    if value <= 0:
      raise serializers.ValidationError("Amount must be greater than zero.")
    return value

class AFOCapCheckSerializer(serializers.Serializer):
  category = serializers.CharField()
  cap_per_acre = serializers.DecimalField(max_digits=10, decimal_places=2)
  total_cap = serializers.DecimalField(max_digits=12, decimal_places=2)
  already_spent = serializers.DecimalField(max_digits=12, decimal_places=2)
  remaining = serializers.DecimalField(max_digits=12, decimal_places=2)
  is_allowed_now = serializers.BooleanField()