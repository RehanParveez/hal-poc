import factory
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from apps.accounts.tests.factories import UserFactory, FarmerProfileFactory, BankProfileFactory
from apps.escrow.tests.factories import CropTypeFactory
from apps.accounts.models import InsuranceProfile
from apps.loans.models import LoanApplication
from apps.escrow.models import EscrowWallet
from apps.insurance.models import InsurancePolicy, InsuranceClaim

class InsuranceProfileFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = InsuranceProfile
    django_get_or_create = ('user',)
  user = factory.SubFactory(UserFactory, role='insurance')
  company_name = 'State Life Insurance'

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

class EscrowWalletFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = EscrowWallet
  loan = factory.SubFactory(LoanApplicationFactory)
  total_funded = Decimal('100000.00')
  remaining_balance = Decimal('100000.00')
  insurance_premium_deducted = Decimal('0')

class InsurancePolicyFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = InsurancePolicy
  loan = factory.SubFactory(LoanApplicationFactory)
  insurer = factory.SubFactory(InsuranceProfileFactory)
  coverage_amount = Decimal('100000.00')
  premium_amount = Decimal('2500.00')
  status = 'active'
  policy_start = factory.LazyFunction(lambda: timezone.now().date())
  policy_end = factory.LazyFunction(lambda: timezone.now().date() + timedelta(days=180))

class InsuranceClaimFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = InsuranceClaim
  policy = factory.SubFactory(InsurancePolicyFactory)
  claimed_by = factory.SelfAttribute('policy.loan.farmer.user')
  reason = 'Crop damaged due to flooding in the region'
  claim_amount = Decimal('30000.00')
  status = 'pending'