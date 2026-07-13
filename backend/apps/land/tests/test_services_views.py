from decimal import Decimal
from apps.accounts.tests.factories import LandownerProfileFactory, UserFactory, FarmerProfileFactory
from apps.land.tests.factories import LandFactory, TenantAgreementFactory
import pytest
from apps.land.services import LandService, TenantAgreementService
from apps.land.models import Land, TenantAgreement
from shared.exceptions import AcreageCeilingExceededError
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.land.views import LandViewSet, TenantAgreementViewSet

def _build_parcel(total_acres=Decimal('10.00')):
  landowner = LandownerProfileFactory()
  return LandFactory(landowner=landowner, total_acres=total_acres)

@pytest.mark.django_db
class TestCreateParcel:
  def test_increments_landowner_total_registered_acres(self):
    landowner = LandownerProfileFactory(total_registered_acres=Decimal('0'))
    parcel = LandService.create_parcel(landowner_profile=landowner, validated_data={
      'parcel_ref': 'PR-001', 'district': 'Faisalabad', 'total_acres': Decimal('12.50')})
    landowner.refresh_from_db()
    assert landowner.total_registered_acres == Decimal('12.50')
    assert parcel.landowner_id == landowner.id
 
  def test_accumulates_across_multiple_parcels(self):
    landowner = LandownerProfileFactory(total_registered_acres=Decimal('0'))
    LandService.create_parcel(landowner_profile=landowner, validated_data={
      'parcel_ref': 'PR-100', 'district': 'Faisalabad', 'total_acres': Decimal('5.00')})
    LandService.create_parcel(landowner_profile=landowner, validated_data={
      'parcel_ref': 'PR-101', 'district': 'Faisalabad', 'total_acres': Decimal('3.00')})
    landowner.refresh_from_db()
    assert landowner.total_registered_acres == Decimal('8.00')
 
  def test_is_atomic_no_orphan_parcel_survives_a_mid_failure(self, monkeypatch):
    landowner = LandownerProfileFactory(total_registered_acres=Decimal('0'))
    def boom(*args, **kwargs):
      raise RuntimeError('simulated failure')
    monkeypatch.setattr(type(landowner), 'save', boom)
    with pytest.raises(RuntimeError):
      LandService.create_parcel(landowner_profile=landowner, validated_data={
        'parcel_ref': 'PR-200', 'district': 'Faisalabad', 'total_acres': Decimal('4.00')})
    assert Land.objects.filter(parcel_ref='PR-200').count() == 0
 
@pytest.mark.django_db
class TestCreateAgreementService:
  def test_rejects_when_leased_acres_exceeds_available_acres(self):
    parcel = _build_parcel(total_acres=Decimal('10.00'))
    tenant = FarmerProfileFactory()
    with pytest.raises(AcreageCeilingExceededError):
      TenantAgreementService.create_agreement(tenant_profile=tenant, parcel_id=parcel.id, validated_data={
        'agreement_type': 'theka', 'leased_acres': Decimal('10.01'), 'season': 'rabi-2026', 'theka_amount': Decimal('50000.00')})
 
  def test_allows_leased_acres_exactly_equal_to_available_acres(self):
    parcel = _build_parcel(total_acres=Decimal('10.00'))
    tenant = FarmerProfileFactory()
    agreement = TenantAgreementService.create_agreement(tenant_profile=tenant, parcel_id=parcel.id, validated_data={
      'agreement_type': 'theka', 'leased_acres': Decimal('10.00'), 'season': 'rabi-2026', 'theka_amount': Decimal('50000.00')})
    assert agreement.leased_acres == Decimal('10.00')
 
  def test_pending_agreements_do_not_reduce_available_acres_for_a_second_request(self):
    parcel = _build_parcel(total_acres=Decimal('10.00'))
    tenant_a = FarmerProfileFactory()
    tenant_b = FarmerProfileFactory()
    TenantAgreementService.create_agreement(tenant_profile=tenant_a, parcel_id=parcel.id, validated_data={
      'agreement_type': 'theka', 'leased_acres': Decimal('9.00'), 'season': 'rabi-2026', 'theka_amount': Decimal('9000.00')})
    parcel.refresh_from_db()
    assert parcel.available_acres == Decimal('10.00')
    second = TenantAgreementService.create_agreement(tenant_profile=tenant_b, parcel_id=parcel.id, validated_data={
      'agreement_type': 'theka', 'leased_acres': Decimal('9.00'), 'season': 'rabi-2026', 'theka_amount': Decimal('9000.00')})
    assert second.leased_acres == Decimal('9.00')
    
@pytest.mark.django_db
class TestApproveAgreement:
  def test_activates_a_pending_agreement(self):
    parcel = _build_parcel()
    tenant = FarmerProfileFactory()
    agreement = TenantAgreementFactory(parcel=parcel, tenant=tenant, status = 'pending', leased_acres=Decimal('4.00'))
    approved = TenantAgreementService.approve_agreement(agreement_id=agreement.id, landowner_profile=parcel.landowner)
    assert approved.status == 'active'
    assert approved.landowner_approved is True
    assert approved.approved_at is not None
 
  def test_rejects_when_caller_does_not_own_the_parcel(self):
    parcel = _build_parcel()
    other_landowner = LandownerProfileFactory()
    agreement = TenantAgreementFactory(parcel=parcel, status = 'pending')
    with pytest.raises(PermissionError):
      TenantAgreementService.approve_agreement(agreement_id=agreement.id, landowner_profile=other_landowner)
 
  def test_rejects_an_already_active_agreement(self):
    parcel = _build_parcel()
    agreement = TenantAgreementFactory(parcel=parcel, status = 'active')
    with pytest.raises(ValueError):
      TenantAgreementService.approve_agreement(agreement_id=agreement.id, landowner_profile=parcel.landowner)
 
  def test_approving_two_pending_agreements_lets_leased_acres_exceed_total_acres(self):
    parcel = _build_parcel(total_acres=Decimal('10.00'))
    agreement_a = TenantAgreementFactory(parcel=parcel, tenant=FarmerProfileFactory(), status = 'pending', leased_acres=Decimal('8.00'))
    agreement_b = TenantAgreementFactory(parcel=parcel, tenant=FarmerProfileFactory(), status = 'pending', leased_acres=Decimal('8.00'))
    TenantAgreementService.approve_agreement(agreement_id=agreement_a.id, landowner_profile=parcel.landowner)
    TenantAgreementService.approve_agreement(agreement_id=agreement_b.id, landowner_profile=parcel.landowner)
    parcel.refresh_from_db()
    assert parcel.available_acres == Decimal('-6.00')
 
@pytest.mark.django_db
class TestRejectAgreement:
  def test_sets_status_and_stores_reason(self):
    parcel = _build_parcel()
    agreement = TenantAgreementFactory(parcel=parcel, status = 'pending')
    rejected = TenantAgreementService.reject_agreement(agreement_id=agreement.id, landowner_profile=parcel.landowner, reason = 'Parcel needed for own use')
    assert rejected.status == 'rejected'
    assert rejected.landowner_approved is False
    assert rejected.rejected_reason == 'Parcel needed for own use'
 
  def test_rejects_when_caller_does_not_own_the_parcel(self):
    parcel = _build_parcel()
    other_landowner = LandownerProfileFactory()
    agreement = TenantAgreementFactory(parcel=parcel, status = 'pending')
    with pytest.raises(PermissionError):
      TenantAgreementService.reject_agreement(agreement_id=agreement.id, landowner_profile=other_landowner)
 
  def test_rejects_an_already_rejected_agreement(self):
    parcel = _build_parcel()
    agreement = TenantAgreementFactory(parcel=parcel, status = 'rejected')
    with pytest.raises(ValueError):
      TenantAgreementService.reject_agreement(agreement_id=agreement.id, landowner_profile=parcel.landowner)
      
@pytest.mark.django_db
class TestLandViewSetPermissions:
  def test_create_is_denied_for_a_tenant_role(self):
    tenant_user = UserFactory(role = 'tenant')
    factory = APIRequestFactory()
    request = factory.post('/', {'parcel_ref': 'X', 'district': 'Faisalabad', 'total_acres': '5.00'})
    force_authenticate(request, user=tenant_user)
    view = LandViewSet.as_view({'post': 'create'})
    response = view(request)
    assert response.status_code == 403

  def test_list_is_denied_for_a_shopkeeper_role(self):
    shopkeeper = UserFactory(role = 'shopkeeper')
    factory = APIRequestFactory()
    request = factory.get('/')
    force_authenticate(request, user=shopkeeper)
    view = LandViewSet.as_view({'get': 'list'})
    response = view(request)
    assert response.status_code == 403

  def test_create_is_rejected_without_authentication(self):
    factory = APIRequestFactory()
    request = factory.post('/', {'parcel_ref': 'X', 'district': 'Faisalabad', 'total_acres': '5.00'})
    view = LandViewSet.as_view({'post': 'create'})
    response = view(request)
    assert response.status_code == 401

@pytest.mark.django_db
class TestLandViewSetQuerysetScoping:
  def test_landowner_only_sees_their_own_parcels(self):
    parcel_a = _build_parcel()
    parcel_b = _build_parcel()
    factory = APIRequestFactory()
    request = factory.get('/')
    force_authenticate(request, user=parcel_a.landowner.user)
    view = LandViewSet.as_view({'get': 'list'})
    response = view(request)
    returned_ids = {row['id'] for row in response.data['results']}
    assert str(parcel_a.id) in returned_ids
    assert str(parcel_b.id) not in returned_ids

  def test_bank_role_sees_parcels_across_all_landowners(self):
    parcel_a = _build_parcel()
    parcel_b = _build_parcel()
    bank_user = UserFactory(role = 'bank')
    factory = APIRequestFactory()
    request = factory.get('/')
    force_authenticate(request, user=bank_user)
    view = LandViewSet.as_view({'get': 'list'})
    response = view(request)
    returned_ids = {row['id'] for row in response.data['results']}
    assert str(parcel_a.id) in returned_ids
    assert str(parcel_b.id) in returned_ids

  def test_district_query_param_filters_for_non_landowner_roles(self):
    parcel_a = _build_parcel()
    parcel_a.district = 'Faisalabad'
    parcel_a.save(update_fields=['district'])
    parcel_b = _build_parcel()
    parcel_b.district = 'Lahore'
    parcel_b.save(update_fields=['district'])
    bank_user = UserFactory(role = 'bank')
    factory = APIRequestFactory()
    request = factory.get('/', {'district': 'Faisalabad'})
    force_authenticate(request, user=bank_user)
    view = LandViewSet.as_view({'get': 'list'})
    response = view(request)
    returned_ids = {row['id'] for row in response.data['results']}
    assert str(parcel_a.id) in returned_ids
    assert str(parcel_b.id) not in returned_ids

@pytest.mark.django_db
class TestLandCreateFlow:
  def test_create_routes_through_the_service_and_updates_registered_acres(self):
    landowner_user = UserFactory(role = 'landowner')
    landowner = landowner_user.landowner_profile
    landowner.total_registered_acres = Decimal('0')
    landowner.save(update_fields=['total_registered_acres'])
    factory = APIRequestFactory()
    request = factory.post('/', {'parcel_ref': 'PR-500', 'district': 'Faisalabad', 'total_acres': '6.25'})
    force_authenticate(request, user=landowner_user)
    view = LandViewSet.as_view({'post': 'create'})
    response = view(request)
    assert response.status_code == 201
    landowner.refresh_from_db()
    assert landowner.total_registered_acres == Decimal('6.25')

  def test_zero_total_acres_is_rejected(self):
    landowner_user = UserFactory(role = 'landowner')
    factory = APIRequestFactory()
    request = factory.post('/', {'parcel_ref': 'PR-501', 'district': 'Faisalabad', 'total_acres': '0'})
    force_authenticate(request, user=landowner_user)
    view = LandViewSet.as_view({'post': 'create'})
    response = view(request)
    assert response.status_code == 400

@pytest.mark.django_db
class TestLandUpdateAndDeleteDoNotSyncRegisteredAcres:
  def test_updating_total_acres_does_not_resync_landowner_registered_acres(self):
    parcel = _build_parcel(total_acres=Decimal('10.00'))
    parcel.landowner.total_registered_acres = Decimal('10.00')
    parcel.landowner.save(update_fields=['total_registered_acres'])
    factory = APIRequestFactory()
    request = factory.patch('/', {'total_acres': '25.00'}, format = 'json')
    force_authenticate(request, user=parcel.landowner.user)
    view = LandViewSet.as_view({'patch': 'partial_update'})
    response = view(request, pk=parcel.id)
    assert response.status_code == 200
    parcel.refresh_from_db()
    parcel.landowner.refresh_from_db()
    assert parcel.total_acres == Decimal('25.00')
    assert parcel.landowner.total_registered_acres == Decimal('10.00')

  def test_deleting_a_parcel_does_not_decrement_landowner_registered_acres(self):
    parcel = _build_parcel(total_acres=Decimal('10.00'))
    parcel.landowner.total_registered_acres = Decimal('10.00')
    parcel.landowner.save(update_fields=['total_registered_acres'])
    factory = APIRequestFactory()
    request = factory.delete('/')
    force_authenticate(request, user=parcel.landowner.user)
    view = LandViewSet.as_view({'delete': 'destroy'})
    response = view(request, pk=parcel.id)
    assert response.status_code == 204
    parcel.landowner.refresh_from_db()
    assert not Land.objects.filter(id=parcel.id).exists()
    assert parcel.landowner.total_registered_acres == Decimal('10.00')

@pytest.mark.django_db
class TestTenantAgreementViewSetAuthenticationGap:
  def test_unauthenticated_list_request_crashes_instead_of_returning_401(self):
    factory = APIRequestFactory()
    request = factory.get('/')
    view = TenantAgreementViewSet.as_view({'get': 'list'})
    response = view(request)
    assert response.status_code in [401, 403]

  def test_unauthenticated_retrieve_request_crashes_instead_of_returning_401(self):
    parcel = _build_parcel()
    agreement = TenantAgreementFactory(parcel=parcel, status = 'pending')
    factory = APIRequestFactory()
    request = factory.get('/')
    view = TenantAgreementViewSet.as_view({'get': 'retrieve'})
    response = view(request, pk=agreement.id)
    assert response.status_code in [401, 403]

@pytest.mark.django_db
class TestTenantAgreementUpdateHasNoPermissionOrCeilingCheck:
  def test_tenant_cannot_raise_their_own_leased_acres_past_the_parcel_ceiling(self):
    parcel = _build_parcel(total_acres=Decimal('10.00'))
    agreement = TenantAgreementFactory(parcel=parcel, status = 'pending', leased_acres=Decimal('5.00'))
    factory = APIRequestFactory()
    request = factory.patch('/', {'leased_acres': '999.00'}, format = 'json')
    force_authenticate(request, user=agreement.tenant.user)
    view = TenantAgreementViewSet.as_view({'patch': 'partial_update'})
    response = view(request, pk=agreement.id)
    assert response.status_code == 403
    agreement.refresh_from_db()
    assert agreement.leased_acres == Decimal('5.00')

  def test_a_bank_user_can_modify_any_active_agreement_platform_wide(self):
    parcel = _build_parcel(total_acres=Decimal('10.00'))
    agreement = TenantAgreementFactory(parcel=parcel, status = 'active', leased_acres=Decimal('5.00'))
    unrelated_bank_user = UserFactory(role = 'bank')
    factory = APIRequestFactory()
    request = factory.patch('/', {'leased_acres': '9.00'}, format = 'json')
    force_authenticate(request, user=unrelated_bank_user)
    view = TenantAgreementViewSet.as_view({'patch': 'partial_update'})
    response = view(request, pk=agreement.id)
    assert response.status_code == 200
    agreement.refresh_from_db()
    assert agreement.leased_acres == Decimal('9.00')

  def test_a_bank_user_can_delete_any_active_agreement_platform_wide(self):
    parcel = _build_parcel()
    agreement = TenantAgreementFactory(parcel=parcel, status = 'active')
    unrelated_bank_user = UserFactory(role = 'bank')
    factory = APIRequestFactory()
    request = factory.delete('/')
    force_authenticate(request, user=unrelated_bank_user)
    view = TenantAgreementViewSet.as_view({'delete': 'destroy'})
    response = view(request, pk=agreement.id)
    assert response.status_code == 204
    assert not TenantAgreement.objects.filter(id=agreement.id).exists()

@pytest.mark.django_db
class TestApproveRejectActions:
  def test_approve_is_denied_for_a_tenant_role(self):
    parcel = _build_parcel()
    agreement = TenantAgreementFactory(parcel=parcel, status = 'pending')
    factory = APIRequestFactory()
    request = factory.patch('/')
    force_authenticate(request, user=agreement.tenant.user)
    view = TenantAgreementViewSet.as_view({'patch': 'approve'})
    response = view(request, pk=agreement.id)
    assert response.status_code == 403

  def test_approve_by_a_non_owning_landowner_returns_400_not_403(self):
    parcel = _build_parcel()
    other_landowner = LandownerProfileFactory()
    agreement = TenantAgreementFactory(parcel=parcel, status = 'pending')
    factory = APIRequestFactory()
    request = factory.patch('/')
    force_authenticate(request, user=other_landowner.user)
    view = TenantAgreementViewSet.as_view({'patch': 'approve'})
    response = view(request, pk=agreement.id)
    assert response.status_code == 400

  def test_approve_returns_404_for_a_nonexistent_agreement(self):
    landowner_user = UserFactory(role = 'landowner')
    factory = APIRequestFactory()
    request = factory.patch('/')
    force_authenticate(request, user=landowner_user)
    view = TenantAgreementViewSet.as_view({'patch': 'approve'})
    response = view(request, pk='00000000-0000-0000-0000-000000000000')
    assert response.status_code == 404

  def test_reject_stores_the_reason_via_the_endpoint(self):
    parcel = _build_parcel()
    agreement = TenantAgreementFactory(parcel=parcel, status = 'pending')
    factory = APIRequestFactory()
    request = factory.patch('/', {'reason': 'Land needed for personal cultivation'}, format = 'json')
    force_authenticate(request, user=parcel.landowner.user)
    view = TenantAgreementViewSet.as_view({'patch': 'reject'})
    response = view(request, pk=agreement.id)
    assert response.status_code == 200
    agreement.refresh_from_db()
    assert agreement.status == 'rejected'
    assert agreement.rejected_reason == 'Land needed for personal cultivation'