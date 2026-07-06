import factory
from decimal import Decimal
from apps.contracts.models import CropContract, FarmerContractAllocation

class CropContractFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = CropContract
  required_kg = Decimal('100000.00')
  allocated_kg = Decimal('0.00')
  base_price_per_kg = Decimal('150.00')
  payment_defer_days = 20
  quality_grade_expected = 'Grade A'
  status = 'open'
  delivery_deadline = factory.Faker('future_date')

class FarmerContractAllocationFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = FarmerContractAllocation
  contract = factory.SubFactory(CropContractFactory)
  committed_kg = Decimal('10000.00')