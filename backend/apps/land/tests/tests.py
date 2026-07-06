import pytest
from apps.land.tests.factories import LandFactory, TenantAgreementFactory
from decimal import Decimal
from django.db import IntegrityError
from apps.land.models import Land, TenantAgreement
from apps.accounts.tests.factories import FarmerProfileFactory, LandownerProfileFactory

@pytest.mark.django_db
class TestLandAvailableAcres:
  def test_available_acres_subtracts_only_active_agreements(self):
    parcel = LandFactory(total_acres=Decimal('20.00'))
    TenantAgreementFactory(parcel=parcel, leased_acres=Decimal('5.00'), status = 'active')
    TenantAgreementFactory(parcel=parcel, leased_acres=Decimal('3.00'), status = 'pending', tenant=FarmerProfileFactory())
    TenantAgreementFactory(parcel=parcel, leased_acres=Decimal('4.00'), status = 'completed', tenant=FarmerProfileFactory())
    assert parcel.available_acres == Decimal('15.00') 

  def test_available_acres_equals_total_when_no_agreements_exist(self):
    parcel = LandFactory(total_acres=Decimal('12.50'))
    assert parcel.available_acres == Decimal('12.50')

  def test_parcel_ref_uniqueness_is_enforced(self):
    LandFactory(parcel_ref = 'PR-UNIQUE-023')
    with pytest.raises(IntegrityError):
      Land.objects.create(landowner=LandownerProfileFactory(), parcel_ref = 'PR-UNIQUE-023',
        district = 'Islamabad', total_acres=Decimal('1.00'))

@pytest.mark.django_db
class TestTenantAgreementConstraints:
  def test_same_tenant_parcel_season_combination_is_rejected(self):
    tenant = FarmerProfileFactory()
    parcel = LandFactory()
    TenantAgreementFactory(tenant=tenant, parcel=parcel, season = 'rabi-2026')
    with pytest.raises(IntegrityError):
      TenantAgreement.objects.create(tenant=tenant, parcel=parcel, season = 'rabi-2026',
        agreement_type = 'batai', leased_acres=Decimal('2.00'))

  def test_same_tenant_and_parcel_different_season_is_allowed(self):
    tenant = FarmerProfileFactory()
    parcel = LandFactory()
    TenantAgreementFactory(tenant=tenant, parcel=parcel, season = 'rabi-2026')
    TenantAgreementFactory(tenant=tenant, parcel=parcel, season = 'kharif-2026')
    assert TenantAgreement.objects.filter(tenant=tenant, parcel=parcel).count() == 2