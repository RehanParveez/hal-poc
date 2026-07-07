from rest_framework import serializers
from apps.crops.models import CropType, CropInputCap, CropLifecycleMilestone

class CropTypeSerializer(serializers.ModelSerializer):
  class Meta:
    model = CropType
    fields = ['id', 'name', 'code', 'season', 'created_at']
    read_only_fields = ['id', 'created_at']

  def validate_code(self, value):
    if not value.strip():
      raise serializers.ValidationError('the crop code cant be blank.')
    return value.upper().strip()

class CropInputCapSerializer(serializers.ModelSerializer):
  crop_name = serializers.CharField(source = 'crop.name', read_only=True)
  crop_code = serializers.CharField(source = 'crop.code', read_only=True)

  class Meta:
    model = CropInputCap
    fields = ['id', 'crop', 'crop_name', 'crop_code', 'district', 'input_category', 'max_cost_per_acre', 'valid_season', 'created_at']
    read_only_fields = ['id', 'created_at', 'crop_name', 'crop_code']
    validators = []

  def validate_max_cost_per_acre(self, value):
    if value <= 0:
      raise serializers.ValidationError('the max cost per acre must be > than zero.')
    return value

class CropLifecycleMilestoneSerializer(serializers.ModelSerializer):
  crop_name = serializers.CharField(source = 'crop.name', read_only=True)
  crop_code = serializers.CharField(source = 'crop.code', read_only=True)

  class Meta:
    model = CropLifecycleMilestone
    fields = ['id', 'crop', 'crop_name', 'crop_code', 'phase_number', 'phase_name', 'day_offset',
      'unlock_pct', 'allowed_input_categories', 'created_at']
    read_only_fields = ['id', 'created_at', 'crop_name', 'crop_code']

  def validate_unlock_pct(self, value):
    if value <= 0 or value > 100:
      raise serializers.ValidationError('unlock perc must be b/w 0 & 100.')
    return value

  def validate_allowed_input_categories(self, value):
    valid = ['seed', 'fertilizer', 'pesticide', 'irrigation', 'labour']
    for cat in value:
      if cat not in valid:
        raise serializers.ValidationError(f"'{cat}' is not a corr input categ. so choose from: {', '.join(valid)}.")
    return value