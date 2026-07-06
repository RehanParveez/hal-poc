import factory
from decimal import Decimal
from django.utils import timezone
from apps.delivery.models import BatchDelivery
from apps.contracts.tests.factories import FarmerContractAllocationFactory

class BatchDeliveryFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = BatchDelivery

  allocation = factory.SubFactory(FarmerContractAllocationFactory)
  batch_kg = Decimal('2500.00')
  expected_payout = Decimal('375000.00')
  actual_payout = factory.LazyAttribute(lambda o: o.expected_payout) 
  grade_received = 'Grade A'
  grade_deduction_pct = Decimal('0.00')
  status = 'in_transit'
  delivered_at = factory.LazyFunction(timezone.now)