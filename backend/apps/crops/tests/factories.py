import factory
from apps.crops.models import CropType, CropInputCap, CropLifecycleMilestone
from decimal import Decimal

class CropTypeFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = CropType
    django_get_or_create = ('code',)
  name = 'Wheat'
  code = factory.Sequence(lambda n: f'WHEAT{n}')
  season = 'rabi'

class CropInputCapFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = CropInputCap
  crop = factory.SubFactory(CropTypeFactory)
  district = 'Faisalabad'
  input_category = 'seed'
  max_cost_per_acre = Decimal('2000.00')
  valid_season = 'rabi'

class CropLifecycleMilestoneFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = CropLifecycleMilestone
  crop = factory.SubFactory(CropTypeFactory)
  phase_number = 1
  phase_name = 'Sowing'
  day_offset = 0
  unlock_pct = Decimal('30.00')
  allowed_input_categories = ['seed']