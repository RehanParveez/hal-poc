import threading
from decimal import Decimal
from queue import Queue
import pytest
from unittest.mock import patch
from django.db import connections
from django.db.models import Sum
from apps.accounts.tests.factories import FactoryProfileFactory, FarmerProfileFactory, UserFactory
from apps.contracts.tests.factories import FarmerContractAllocationFactory
from apps.delivery.models import BatchDelivery
from apps.delivery.services import BatchDeliveryService
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.delivery.views import BatchDeliveryViewSet
import uuid

def make_batch(allocation, batch_kg=Decimal('50.00'), status='in_transit', **extra):
  expected_payout = (batch_kg * allocation.contract.base_price_per_kg).quantize(Decimal('0.01'))
  return BatchDelivery.objects.create(allocation=allocation, batch_kg=batch_kg, expected_payout=expected_payout,
    status=status, **extra)

@pytest.mark.django_db
class TestLogDelivery:
  def test_creates_batch_with_correct_expected_payout(self):
    allocation = FarmerContractAllocationFactory(committed_kg=Decimal('100.00'))
    allocation.contract.base_price_per_kg = Decimal('50.00')
    allocation.contract.save()
    batch = BatchDeliveryService.log_delivery(allocation.farmer, allocation, Decimal('10.00'))
    assert batch.expected_payout == Decimal('500.00')
    assert batch.status == 'in_transit'

  def test_rejects_delivery_from_a_farmer_who_does_not_own_the_allocation(self):
    allocation = FarmerContractAllocationFactory()
    other_farmer = FarmerProfileFactory()
    with pytest.raises(PermissionError):
      BatchDeliveryService.log_delivery(other_farmer, allocation, Decimal('10.00'))

  def test_rejects_when_cumulative_delivery_would_exceed_committed_kg(self):
    allocation = FarmerContractAllocationFactory(committed_kg=Decimal('100.00'))
    make_batch(allocation, batch_kg=Decimal('60.00'))
    with pytest.raises(ValueError):
      BatchDeliveryService.log_delivery(allocation.farmer, allocation, Decimal('41.00'))

  def test_allows_delivery_that_lands_exactly_on_the_committed_kg_boundary(self):
    allocation = FarmerContractAllocationFactory(committed_kg=Decimal('100.00'))
    make_batch(allocation, batch_kg=Decimal('60.00'))
    batch = BatchDeliveryService.log_delivery(allocation.farmer, allocation, Decimal('40.00'))
    assert batch.batch_kg == Decimal('40.00')

  def test_cumulative_check_accounts_for_multiple_prior_batches(self):
    allocation = FarmerContractAllocationFactory(committed_kg=Decimal('100.00'))
    make_batch(allocation, batch_kg=Decimal('30.00'))
    make_batch(allocation, batch_kg=Decimal('30.00'))
    make_batch(allocation, batch_kg=Decimal('30.00'))
    with pytest.raises(ValueError):
      BatchDeliveryService.log_delivery(allocation.farmer, allocation, Decimal('11.00')) 

  def test_negative_batch_kg_is_not_rejected_by_the_service_layer(self):
    allocation = FarmerContractAllocationFactory(committed_kg=Decimal('100.00'))
    batch = BatchDeliveryService.log_delivery(allocation.farmer, allocation, Decimal('-10.00'))
    assert batch.batch_kg == Decimal('-10.00')
    assert batch.expected_payout == Decimal('-500.00')

  def test_expected_payout_rounding_is_currently_bankers_rounding(self):
    allocation = FarmerContractAllocationFactory(committed_kg=Decimal('1000.00'))
    allocation.contract.base_price_per_kg = Decimal('0.01')
    allocation.contract.save()
    batch = BatchDeliveryService.log_delivery(allocation.farmer, allocation, Decimal('12.5'))
    assert batch.expected_payout == Decimal('0.12')
    
@pytest.mark.django_db(transaction=True)
class TestLogDeliveryConcurrency:
  def test_concurrent_deliveries_can_jointly_exceed_committed_kg(self):
    allocation = FarmerContractAllocationFactory(committed_kg=Decimal('100.00'))
    farmer = allocation.farmer
    barrier = threading.Barrier(2)
    results = Queue()

    def worker():
      barrier.wait()
      try:
        BatchDeliveryService.log_delivery(farmer, allocation, Decimal('60.00'))
        results.put('success')
      except ValueError:
        results.put('failure')
      finally:
        connections.close_all()
    threads = [threading.Thread(target=worker) for _ in range(2)]
    for t in threads: t.start()
    for t in threads: t.join()

    outcomes = list(results.queue)
    assert outcomes.count('success') == 2, (
      f"expected both to succeed (proving the missing lock), got: {outcomes} -- "
      "if this ever fails, a lock may already be in place")
    total = BatchDelivery.objects.filter(allocation=allocation).aggregate(total=Sum('batch_kg'))['total']
    assert total == Decimal('120.00') > allocation.committed_kg

@pytest.mark.django_db
class TestMarkReceived:
  def test_transitions_in_transit_batch_to_received(self):
    allocation = FarmerContractAllocationFactory()
    batch = make_batch(allocation, status = 'in_transit')
    updated = BatchDeliveryService.mark_received(batch.id, allocation.contract.factory)
    assert updated.status == 'received'

  def test_rejects_a_factory_that_does_not_own_the_contract(self):
    allocation = FarmerContractAllocationFactory()
    batch = make_batch(allocation, status = 'in_transit')
    with pytest.raises(PermissionError):
      BatchDeliveryService.mark_received(batch.id, FactoryProfileFactory())

  @pytest.mark.parametrize("bad_status", ['received', 'grade_confirmed', 'payment_triggered'])
  def test_rejects_batches_not_currently_in_transit(self, bad_status):
    allocation = FarmerContractAllocationFactory()
    batch = make_batch(allocation, status=bad_status)
    with pytest.raises(ValueError):
      BatchDeliveryService.mark_received(batch.id, allocation.contract.factory)

@pytest.mark.django_db
class TestConfirmGradeGuardRails:
  def test_rejects_a_factory_that_does_not_own_the_contract(self):
    allocation = FarmerContractAllocationFactory()
    batch = make_batch(allocation, status='in_transit')
    with pytest.raises(PermissionError):
      BatchDeliveryService.confirm_grade(batch.id, FactoryProfileFactory(), 'A', Decimal('5.00'))

  @pytest.mark.parametrize("bad_status", ['grade_confirmed', 'payment_triggered'])
  def test_rejects_batches_already_past_grade_confirmation(self, bad_status):
    allocation = FarmerContractAllocationFactory()
    batch = make_batch(allocation, status=bad_status)
    with pytest.raises(ValueError):
      BatchDeliveryService.confirm_grade(batch.id, allocation.contract.factory, 'A', Decimal('5.00'))

  @pytest.mark.parametrize("allowed_status", ['in_transit', 'received'])
  def test_allows_grading_from_either_in_transit_or_received(self, allowed_status):
    allocation = FarmerContractAllocationFactory()
    batch = make_batch(allocation, status=allowed_status)
    with patch('apps.delivery.services.SettlementService.execute_settlement'):
      result = BatchDeliveryService.confirm_grade(batch.id, allocation.contract.factory, 'A', Decimal('5.00'))
    assert result.status == 'grade_confirmed'
    
@pytest.mark.django_db
class TestConfirmGradePayoutMathAndSettlementHandoff:
  def test_zero_deduction_leaves_actual_payout_equal_to_expected(self):
    allocation = FarmerContractAllocationFactory()
    batch = make_batch(allocation)
    batch.expected_payout = Decimal('500.00')
    batch.save()
    with patch('apps.delivery.services.SettlementService.execute_settlement'):
      result = BatchDeliveryService.confirm_grade(batch.id, allocation.contract.factory, 'A', Decimal('0.00'))
    assert result.actual_payout == Decimal('500.00')

  def test_full_deduction_zeroes_out_actual_payout(self):
    allocation = FarmerContractAllocationFactory()
    batch = make_batch(allocation)
    batch.expected_payout = Decimal('500.00')
    batch.save()
    with patch('apps.delivery.services.SettlementService.execute_settlement'):
      result = BatchDeliveryService.confirm_grade(batch.id, allocation.contract.factory, 'C', Decimal('100.00'))
    assert result.actual_payout == Decimal('0.00')

  def test_partial_deduction_computes_correctly(self):
    allocation = FarmerContractAllocationFactory()
    batch = make_batch(allocation)
    batch.expected_payout = Decimal('1000.00')
    batch.save()
    with patch('apps.delivery.services.SettlementService.execute_settlement'):
      result = BatchDeliveryService.confirm_grade(batch.id, allocation.contract.factory, 'B', Decimal('15.00'))
    assert result.actual_payout == Decimal('850.00')

  def test_grade_fields_and_timestamp_are_persisted(self):
    allocation = FarmerContractAllocationFactory()
    batch = make_batch(allocation)
    with patch('apps.delivery.services.SettlementService.execute_settlement'):
      result = BatchDeliveryService.confirm_grade(batch.id, allocation.contract.factory, 'B+', Decimal('8.00'), grade_notes = 'minor moisture damage')
    assert result.grade_received == 'B+'
    assert result.grade_deduction_pct == Decimal('8.00')
    assert result.grade_notes == 'minor moisture damage'
    assert result.grade_confirmed_at is not None

  def test_settlement_service_is_invoked_exactly_once_with_this_batch(self):
    allocation = FarmerContractAllocationFactory()
    batch = make_batch(allocation)
    with patch('apps.delivery.services.SettlementService.execute_settlement') as mock_execute:
      BatchDeliveryService.confirm_grade(batch.id, allocation.contract.factory, 'A', Decimal('5.00'))
    mock_execute.assert_called_once()
    assert mock_execute.call_args[0][0].id == batch.id


def make_batch(allocation, batch_kg=Decimal('50.00'), status='in_transit', **extra):
  expected_payout = (batch_kg * allocation.contract.base_price_per_kg).quantize(Decimal('0.01'))
  return BatchDelivery.objects.create(allocation=allocation, batch_kg=batch_kg, expected_payout=expected_payout, 
    status=status, **extra)

@pytest.mark.django_db
class TestCreatePermissionsAndValidation:
  def test_non_farmer_role_is_blocked_from_creating(self):
    allocation = FarmerContractAllocationFactory()
    shopkeeper = UserFactory(role='shopkeeper')
    req = APIRequestFactory().post('/delivery/batches/', {'allocation': str(allocation.id), 'batch_kg': '10.00'})
    force_authenticate(req, user=shopkeeper)
    assert BatchDeliveryViewSet.as_view({'post': 'create'})(req).status_code == 403

  def test_farmer_can_log_a_valid_delivery(self):
    allocation = FarmerContractAllocationFactory()
    req = APIRequestFactory().post('/delivery/batches/', {'allocation': str(allocation.id), 'batch_kg': '10.00'})
    force_authenticate(req, user=allocation.farmer.user)
    assert BatchDeliveryViewSet.as_view({'post': 'create'})(req).status_code == 201

  def test_farmer_cannot_log_a_delivery_against_someone_else_s_allocation(self):
    allocation = FarmerContractAllocationFactory()
    other_farmer_user = UserFactory(role='smallholder')
    req = APIRequestFactory().post('/delivery/batches/', {'allocation': str(allocation.id), 'batch_kg': '10.00'})
    force_authenticate(req, user=other_farmer_user)
    assert BatchDeliveryViewSet.as_view({'post': 'create'})(req).status_code == 403

  def test_non_numeric_batch_kg_returns_a_clean_400(self):
    allocation = FarmerContractAllocationFactory()
    req = APIRequestFactory().post('/delivery/batches/', {'allocation': str(allocation.id), 'batch_kg': 'not-a-number'})
    force_authenticate(req, user=allocation.farmer.user)
    assert BatchDeliveryViewSet.as_view({'post': 'create'})(req).status_code == 400

  def test_zero_batch_kg_is_blocked_but_only_by_accident(self):
    allocation = FarmerContractAllocationFactory()
    req = APIRequestFactory().post('/delivery/batches/', {'allocation': str(allocation.id), 'batch_kg': '0'})
    force_authenticate(req, user=allocation.farmer.user)
    assert BatchDeliveryViewSet.as_view({'post': 'create'})(req).status_code == 400

  def test_negative_batch_kg_is_accepted_through_the_api(self):
    allocation = FarmerContractAllocationFactory()
    req = APIRequestFactory().post('/delivery/batches/', {'allocation': str(allocation.id), 'batch_kg': '-25.00'})
    force_authenticate(req, user=allocation.farmer.user)
    response = BatchDeliveryViewSet.as_view({'post': 'create'})(req)
    assert response.status_code == 201, "if this now 400s, the gap has been fixed -- update this test"
    assert Decimal(response.data['batch_kg']) == Decimal('-25.00')

  def test_missing_allocation_id_returns_400(self):
    farmer_user = UserFactory(role='smallholder')
    req = APIRequestFactory().post('/delivery/batches/', {'batch_kg': '10.00'})
    force_authenticate(req, user=farmer_user)
    assert BatchDeliveryViewSet.as_view({'post': 'create'})(req).status_code == 400

  def test_nonexistent_allocation_id_returns_404(self):
    farmer_user = UserFactory(role='smallholder')
    req = APIRequestFactory().post('/delivery/batches/', {'allocation': str(uuid.uuid4()), 'batch_kg': '10.00'})
    force_authenticate(req, user=farmer_user)
    assert BatchDeliveryViewSet.as_view({'post': 'create'})(req).status_code == 404
    
@pytest.mark.django_db
class TestQuerysetScoping:
  def test_farmer_sees_only_their_own_batches(self):
    allocation = FarmerContractAllocationFactory()
    other_allocation = FarmerContractAllocationFactory()
    my_batch = make_batch(allocation)
    make_batch(other_allocation)
    req = APIRequestFactory().get('/delivery/batches/')
    force_authenticate(req, user=allocation.farmer.user)
    response = BatchDeliveryViewSet.as_view({'get': 'list'})(req)
    assert {row['id'] for row in response.data['results']} == {str(my_batch.id)}

  def test_factory_sees_only_batches_under_their_own_contracts(self):
    allocation = FarmerContractAllocationFactory()
    other_allocation = FarmerContractAllocationFactory()
    my_batch = make_batch(allocation)
    make_batch(other_allocation)
    req = APIRequestFactory().get('/delivery/batches/')
    force_authenticate(req, user=allocation.contract.factory.user)
    response = BatchDeliveryViewSet.as_view({'get': 'list'})(req)
    assert {row['id'] for row in response.data['results']} == {str(my_batch.id)}

  def test_unrelated_role_sees_nothing(self):
    allocation = FarmerContractAllocationFactory()
    make_batch(allocation)
    shopkeeper = UserFactory(role = 'shopkeeper')
    req = APIRequestFactory().get('/delivery/batches/')
    force_authenticate(req, user=shopkeeper)
    response = BatchDeliveryViewSet.as_view({'get': 'list'})(req)
    assert response.data['results'] == []
    
@pytest.mark.django_db
class TestActionPermissions:
  def test_non_factory_role_blocked_from_mark_received(self):
    allocation = FarmerContractAllocationFactory()
    batch = make_batch(allocation, status='in_transit')
    req = APIRequestFactory().patch(f'/delivery/batches/{batch.id}/mark_received/')
    force_authenticate(req, user=allocation.farmer.user)
    response = BatchDeliveryViewSet.as_view({'patch': 'mark_received'})(req, pk=str(batch.id))
    assert response.status_code == 403

  def test_different_factory_blocked_from_mark_received(self):
    allocation = FarmerContractAllocationFactory()
    batch = make_batch(allocation, status = 'in_transit')
    other_factory_user = UserFactory(role = 'factory')
    req = APIRequestFactory().patch(f'/delivery/batches/{batch.id}/mark_received/')
    force_authenticate(req, user=other_factory_user)
    response = BatchDeliveryViewSet.as_view({'patch': 'mark_received'})(req, pk=str(batch.id))
    assert response.status_code == 403

  def test_owning_factory_can_mark_received(self):
    allocation = FarmerContractAllocationFactory()
    batch = make_batch(allocation, status = 'in_transit')
    req = APIRequestFactory().patch(f'/delivery/batches/{batch.id}/mark_received/')
    force_authenticate(req, user=allocation.contract.factory.user)
    response = BatchDeliveryViewSet.as_view({'patch': 'mark_received'})(req, pk=str(batch.id))
    assert response.status_code == 200
    assert response.data['batch']['status'] == 'received'

  def test_non_factory_role_blocked_from_confirm_grade(self):
    allocation = FarmerContractAllocationFactory()
    batch = make_batch(allocation, status = 'in_transit')
    req = APIRequestFactory().patch(f'/delivery/batches/{batch.id}/confirm_grade/', {'grade_received': 'A', 'grade_deduction_pct': '5.00'})
    force_authenticate(req, user=allocation.farmer.user)
    response = BatchDeliveryViewSet.as_view({'patch': 'confirm_grade'})(req, pk=str(batch.id))
    assert response.status_code == 403

  def test_owning_factory_can_confirm_grade(self):
    allocation = FarmerContractAllocationFactory()
    batch = make_batch(allocation, status = 'in_transit')
    req = APIRequestFactory().patch(f'/delivery/batches/{batch.id}/confirm_grade/', {'grade_received': 'A', 'grade_deduction_pct': '5.00'})
    force_authenticate(req, user=allocation.contract.factory.user)
    with patch('apps.delivery.services.SettlementService.execute_settlement'):
      response = BatchDeliveryViewSet.as_view({'patch': 'confirm_grade'})(req, pk=str(batch.id))
    assert response.status_code == 200

  def test_grade_deduction_pct_over_100_is_rejected(self):
    allocation = FarmerContractAllocationFactory()
    batch = make_batch(allocation, status = 'in_transit')
    req = APIRequestFactory().patch(f'/delivery/batches/{batch.id}/confirm_grade/', {'grade_received': 'A', 'grade_deduction_pct': '150.00'})
    force_authenticate(req, user=allocation.contract.factory.user)
    response = BatchDeliveryViewSet.as_view({'patch': 'confirm_grade'})(req, pk=str(batch.id))
    assert response.status_code == 400

  def test_negative_grade_deduction_pct_is_rejected(self):
    allocation = FarmerContractAllocationFactory()
    batch = make_batch(allocation, status = 'in_transit')
    req = APIRequestFactory().patch(f'/delivery/batches/{batch.id}/confirm_grade/', {'grade_received': 'A', 'grade_deduction_pct': '-5.00'})
    force_authenticate(req, user=allocation.contract.factory.user)
    response = BatchDeliveryViewSet.as_view({'patch': 'confirm_grade'})(req, pk=str(batch.id))
    assert response.status_code == 400

  def test_any_authenticated_role_cannot_overwrite_batch_kg_on_someone_else_s_batch(self):
    allocation = FarmerContractAllocationFactory(committed_kg=Decimal('50.00'))
    batch = make_batch(allocation, batch_kg=Decimal('10.00'))
    shopkeeper = UserFactory(role = 'shopkeeper')
    req = APIRequestFactory().patch(f'/delivery/batches/{batch.id}/', {'batch_kg': '99999.00'})
    force_authenticate(req, user=shopkeeper)
    response = BatchDeliveryViewSet.as_view({'patch': 'partial_update'})(req, pk=str(batch.id))
    assert response.status_code == 403
    batch.refresh_from_db()
    assert batch.batch_kg == Decimal('10.00')

  def test_batch_cannot_be_reassigned_to_a_completely_different_allocation(self):
    allocation_a = FarmerContractAllocationFactory()
    allocation_b = FarmerContractAllocationFactory()
    batch = make_batch(allocation_a)
    shopkeeper = UserFactory(role = 'shopkeeper')
    req = APIRequestFactory().patch(f'/delivery/batches/{batch.id}/', {'allocation': str(allocation_b.id)})
    force_authenticate(req, user=shopkeeper)
    response = BatchDeliveryViewSet.as_view({'patch': 'partial_update'})(req, pk=str(batch.id))
    assert response.status_code == 403
    batch.refresh_from_db()
    assert str(batch.allocation_id) == str(allocation_a.id)

  def test_delete_and_put_are_blocked_at_the_http_method_level(self):
    allocation = FarmerContractAllocationFactory()
    batch = make_batch(allocation)
    shopkeeper = UserFactory(role = 'shopkeeper')
    req = APIRequestFactory().delete(f'/delivery/batches/{batch.id}/')
    force_authenticate(req, user=shopkeeper)
    response = BatchDeliveryViewSet.as_view({'delete': 'destroy'})(req, pk=str(batch.id))
    assert response.status_code == 405