from django.db import transaction
from apps.crops.models import CropType, CropInputCap, CropLifecycleMilestone

class CropTypeService:
  @staticmethod
  def create_crop(validated_data):
    with transaction.atomic():
      crop = CropType.objects.create(**validated_data)
      return crop

  @staticmethod
  def update_crop(crop, validated_data):
    with transaction.atomic():
      for field, value in validated_data.items():
        setattr(crop, field, value)
      crop.save()
      return crop

class CropInputCapService:
  @staticmethod
  def set_cap(validated_data):
    crop = validated_data.get('crop')
    district = validated_data.get('district')
    input_category = validated_data.get('input_category')
    valid_season = validated_data.get('valid_season')

    with transaction.atomic():
      cap, created = CropInputCap.objects.update_or_create(crop=crop, district=district, input_category=input_category,
        valid_season=valid_season, defaults={'max_cost_per_acre': validated_data.get('max_cost_per_acre')})
      return cap, created

class CropLifecycleMilestoneService:
  @staticmethod
  def set_milestone(validated_data):
    crop = validated_data.get('crop')
    phase_number = validated_data.get('phase_number')
    with transaction.atomic():
      milestone, created = CropLifecycleMilestone.objects.update_or_create(crop=crop, phase_number=phase_number,
        defaults={'phase_name': validated_data.get('phase_name'), 'day_offset': validated_data.get('day_offset'),
          'unlock_pct': validated_data.get('unlock_pct'), 'allowed_input_categories': validated_data.get('allowed_input_categories')})
      return milestone, created