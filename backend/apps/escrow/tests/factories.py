import factory
from decimal import Decimal
from apps.accounts.tests.factories import FarmerProfileFactory, BankProfileFactory
from apps.loans.models import LoanApplication
from apps.crops.models import CropType, CropLifecycleMilestone, CropInputCap
from apps.escrow.services import EscrowCreationService

class CropTypeFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = CropType
    django_get_or_create = ('code',)
  name = 'Wheat'
  code = 'WHEAT'
  season = 'rabi'

class CropLifecycleMilestoneFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = CropLifecycleMilestone
    django_get_or_create = ('crop', 'phase_number')
  crop = factory.SubFactory(CropTypeFactory)
  phase_number = 1
  phase_name = 'sowing'
  day_offset = 30
  unlock_pct = Decimal('30.00')
  allowed_input_categories = ['seed']

class CropInputCapFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = CropInputCap
    django_get_or_create = ('crop', 'district', 'input_category', 'valid_season')
  crop = factory.SubFactory(CropTypeFactory)
  district = 'Faisalabad'
  input_category = 'seed'
  valid_season = 'rabi'
  max_cost_per_acre = Decimal('2000.00')

class LoanApplicationFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = LoanApplication
  farmer = factory.SubFactory(FarmerProfileFactory)
  bank = factory.SubFactory(BankProfileFactory)
  crop = factory.SubFactory(CropTypeFactory)
  acres_applied_for = Decimal('5.00')
  requested_amount = Decimal('100000.00')
  approved_amount = Decimal('100000.00')
  status = 'disbursed'
  tenant_agreement = None

def build_escrow(unlock_pct=Decimal('30.00'), allowed=('seed',), cap_per_acre=Decimal('2000.00'),
    acres=Decimal('5.00'), approved=Decimal('100000.00')):
  loan = LoanApplicationFactory(approved_amount=approved, acres_applied_for=acres)
  CropLifecycleMilestoneFactory(crop=loan.crop, phase_number=1, unlock_pct=unlock_pct, allowed_input_categories=list(allowed))
  CropInputCapFactory(crop=loan.crop, district=loan.farmer.user.district, input_category = 'seed',
    valid_season=loan.crop.season, max_cost_per_acre=cap_per_acre)
  return EscrowCreationService.create(loan)