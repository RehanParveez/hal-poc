import factory as factory_boy
from apps.accounts.tests.factories import FarmerProfileFactory, FactoryProfileFactory
from apps.contracts.models import CropContract, FarmerContractAllocation
from apps.crops.tests.factories import CropTypeFactory
from decimal import Decimal
from datetime import date, timedelta
from apps.loans.tests.factories import LoanApplicationFactory

class CropContractFactory(factory_boy.django.DjangoModelFactory):
  class Meta:
    model = CropContract
  factory = factory_boy.SubFactory(FactoryProfileFactory)
  crop = factory_boy.SubFactory(CropTypeFactory)
  required_kg = Decimal('10000.00')
  base_price_per_kg = Decimal('50.00')
  delivery_deadline = date.today() + timedelta(days=90)

class FarmerContractAllocationFactory(factory_boy.django.DjangoModelFactory):
  class Meta:
    model = FarmerContractAllocation
  contract = factory_boy.SubFactory(CropContractFactory)
  farmer = factory_boy.SubFactory(FarmerProfileFactory)
  loan = factory_boy.SubFactory(LoanApplicationFactory)
  committed_kg = Decimal('10000.00')