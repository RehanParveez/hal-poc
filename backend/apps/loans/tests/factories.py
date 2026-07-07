import factory
from decimal import Decimal
from apps.loans.models import LoanApplication
from apps.accounts.tests.factories import FarmerProfileFactory, BankProfileFactory
from apps.crops.tests.factories import CropTypeFactory

class LoanApplicationFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = LoanApplication
  farmer = factory.SubFactory(FarmerProfileFactory)
  bank = factory.SubFactory(BankProfileFactory)
  crop = factory.SubFactory(CropTypeFactory)
  acres_applied_for = Decimal('5.00')
  requested_amount = Decimal('100000.00')
  status = 'submitted'