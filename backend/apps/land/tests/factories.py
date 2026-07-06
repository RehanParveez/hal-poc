from apps.land.models import Land, TenantAgreement
import factory
from decimal import Decimal
from apps.accounts.tests.factories import LandownerProfileFactory, FarmerProfileFactory

class LandFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = Land
    django_get_or_create = ('parcel_ref',)
  landowner = factory.SubFactory(LandownerProfileFactory)
  parcel_ref = factory.Sequence(lambda n: f"PR-{n:05d}")
  district = 'Faisalabad'
  total_acres = Decimal('20.00')

class TenantAgreementFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = TenantAgreement
  tenant = factory.SubFactory(FarmerProfileFactory)
  parcel = factory.SubFactory(LandFactory)
  agreement_type = 'theka'
  leased_acres = Decimal('5.00')
  season = 'rabi-2026'
  theka_amount = Decimal('30000.00')
  status = 'active'
  
class LandParcelFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = Land 
  parcel_ref = factory.Sequence(lambda n: f"PARCEL-{n}")
  district = 'Faisalabad'
  tehsil = 'City'
  total_acres = Decimal('12.50')
  arazi_verified = True