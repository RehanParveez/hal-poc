from rest_framework.test import APIRequestFactory, force_authenticate
from apps.escrow.views import EscrowWalletViewSet
import pytest
from apps.escrow.tests.factories import build_escrow
from apps.accounts.tests.factories import UserFactory
from decimal import Decimal, ROUND_DOWN
from apps.escrow.models import EscrowTransaction

def get_authed_view(action_map, user, path='/'):
  factory = APIRequestFactory()
  request = factory.get(path)
  force_authenticate(request, user=user)
  view = EscrowWalletViewSet.as_view(action_map)
  return view, request

@pytest.mark.django_db
class TestEscrowWalletViewSetPermissionClasses:
  def test_shopkeeper_role_is_denied_at_the_permission_layer(self):
    escrow = build_escrow()
    shopkeeper = UserFactory(role = 'shopkeeper')
    view, request = get_authed_view({'get': 'balance'}, shopkeeper)
    response = view(request, pk=escrow.id)
    assert response.status_code == 403

  def test_insurance_role_is_denied_at_the_permission_layer(self):
    escrow = build_escrow()
    insurance_user = UserFactory(role = 'insurance')
    view, request = get_authed_view({'get': 'balance'}, insurance_user)
    response = view(request, pk=escrow.id)
    assert response.status_code == 403

  def test_unauthenticated_request_is_rejected(self):
    escrow = build_escrow()
    factory = APIRequestFactory()
    request = factory.get('/')
    view = EscrowWalletViewSet.as_view({'get': 'balance'})
    response = view(request, pk=escrow.id)
    assert response.status_code == 401

@pytest.mark.django_db
class TestEscrowWalletViewSetGetObjectScoping:
  def test_owning_farmer_can_access_their_own_escrow(self):
    escrow = build_escrow()
    view, request = get_authed_view({'get': 'balance'}, escrow.loan.farmer.user)
    response = view(request, pk=escrow.id)
    assert response.status_code == 200

  def test_a_different_farmer_is_denied_access(self):
    escrow = build_escrow()
    other_farmer = UserFactory(role = 'smallholder')
    view, request = get_authed_view({'get': 'balance'}, other_farmer)
    response = view(request, pk=escrow.id)
    assert response.status_code == 403

  def test_bank_user_from_a_different_bank_is_denied_access(self):
    escrow = build_escrow()
    unrelated_bank_user = UserFactory(role = 'bank')
    view, request = get_authed_view({'get': 'balance'}, unrelated_bank_user)
    response = view(request, pk=escrow.id)
    assert response.status_code == 403

  def test_the_actual_issuing_bank_can_access_the_escrow(self):
    escrow = build_escrow()
    view, request = get_authed_view({'get': 'balance'}, escrow.loan.bank.user)
    response = view(request, pk=escrow.id)
    assert response.status_code == 200

@pytest.mark.django_db
class TestTransactionsAction:
  def test_returns_only_transactions_belonging_to_this_escrow(self):
    escrow = build_escrow()
    other_escrow = build_escrow()
    shopkeeper = UserFactory(role='shopkeeper')
    EscrowTransaction.objects.create(escrow=escrow, txn_type='input', amount=Decimal('100.00'),
      recipient=shopkeeper, input_category='seed')
    EscrowTransaction.objects.create(escrow=other_escrow, txn_type='input', amount=Decimal('200.00'),
      recipient=shopkeeper, input_category='seed')
    view, request = get_authed_view({'get': 'transactions'}, escrow.loan.farmer.user)
    response = view(request, pk=escrow.id)
    assert response.status_code == 200
    assert response.data['count'] == 2
    assert response.data['escrow_id'] == str(escrow.id)
    
  def test_txn_type_query_param_filters_the_results(self):
    escrow = build_escrow()
    shopkeeper = UserFactory(role = 'shopkeeper')
    EscrowTransaction.objects.create(escrow=escrow, txn_type = 'input', amount=Decimal('100.00'),
      recipient=shopkeeper, input_category = 'seed')
    factory = APIRequestFactory()
    request = factory.get('/', {'txn_type': 'input'})
    force_authenticate(request, user=escrow.loan.farmer.user)
    view = EscrowWalletViewSet.as_view({'get': 'transactions'})
    response = view(request, pk=escrow.id)
    assert response.data['count'] == 1

  def test_a_different_farmer_cannot_reach_the_transactions_action_either(self):
    escrow = build_escrow()
    other_farmer = UserFactory(role = 'smallholder')
    view, request = get_authed_view({'get': 'transactions'}, other_farmer)
    response = view(request, pk=escrow.id)
    assert response.status_code == 403

@pytest.mark.django_db
class TestAfoCapsAction:
  def test_currently_allowed_reflects_the_active_phase_s_categories(self):
    escrow = build_escrow(allowed=('seed', 'fertilizer'))
    view, request = get_authed_view({'get': 'afo_caps'}, escrow.loan.farmer.user)
    response = view(request, pk=escrow.id)
    assert response.status_code == 200
    assert set(response.data['currently_allowed']) == {'seed', 'fertilizer'}
    assert response.data['active_phase'] == 'sowing'

  def test_currently_allowed_is_empty_and_active_phase_is_none_with_no_active_unlock(self):
    escrow = build_escrow()
    escrow.unlocks.update(is_active=False)
    view, request = get_authed_view({'get': 'afo_caps'}, escrow.loan.farmer.user)
    response = view(request, pk=escrow.id)
    assert response.status_code == 200
    assert response.data['currently_allowed'] == []
    assert response.data['active_phase'] is None

  def test_already_spent_reflects_only_that_category_s_input_transactions(self):
    escrow = build_escrow(cap_per_acre=Decimal('2000.00'), acres=Decimal('5.00'))
    shopkeeper = UserFactory(role = 'shopkeeper')
    EscrowTransaction.objects.create(escrow=escrow, txn_type = 'input', amount=Decimal('300.00'),
      recipient=shopkeeper, input_category = 'seed')
    EscrowTransaction.objects.create(escrow=escrow, txn_type = 'insurance', amount=Decimal('999.00'),
      recipient=escrow.loan.bank.user, input_category='')  
    view, request = get_authed_view({'get': 'afo_caps'}, escrow.loan.farmer.user)
    response = view(request, pk=escrow.id)
    seed_cap = next(c for c in response.data['caps'] if c['category'] == 'seed')
    assert Decimal(seed_cap['already_spent']) == Decimal('300.00')
    assert Decimal(seed_cap['total_cap']) == Decimal('10000.00')
    assert Decimal(seed_cap['remaining']) == Decimal('9700.00')

  def test_total_cap_rounding_diverges_from_what_process_payment_actually_enforces(self):
    escrow = build_escrow(cap_per_acre=Decimal('18.10'), acres=Decimal('5.55'))
    view, request = get_authed_view({'get': 'afo_caps'}, escrow.loan.farmer.user)
    response = view(request, pk=escrow.id)
    seed_cap = next(c for c in response.data['caps'] if c['category'] == 'seed')
    enforced_cap = (Decimal('18.10') * Decimal('5.55')).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
    assert enforced_cap == Decimal('100.45')
    assert Decimal(seed_cap['total_cap']) == Decimal('100.46')
    assert Decimal(seed_cap['total_cap']) != enforced_cap  

  def test_a_different_farmer_cannot_reach_afo_caps_either(self):
    escrow = build_escrow()
    other_farmer = UserFactory(role = 'smallholder')
    view, request = get_authed_view({'get': 'afo_caps'}, other_farmer)
    response = view(request, pk=escrow.id)
    assert response.status_code == 403