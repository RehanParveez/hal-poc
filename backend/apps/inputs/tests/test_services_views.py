from decimal import Decimal
from apps.loans.tests.factories import LoanApplicationFactory
from apps.crops.tests.factories import CropLifecycleMilestoneFactory, CropInputCapFactory
from apps.escrow.services import EscrowCreationService
import pytest
from shared.exceptions import WrongPhaseForCategoryError
from apps.inputs.services import process_input_request
from apps.accounts.tests.factories import ShopkeeperProfileFactory
from shared.exceptions import NoActivePhaseError
from shared.exceptions import AFOLimitExceededError
from shared.exceptions import NotEnoughEscrowError
from apps.escrow.services import InputPaymentService
from factory.django import mute_signals
from django.db.models.signals import post_save
from apps.accounts.tests.factories import UserFactory
from apps.accounts.models import ShopkeeperProfile
from apps.wallets.models import Wallet
from apps.escrow.models import EscrowWallet
from apps.inputs.models import InputSupplyRequest
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from apps.accounts.tests.factories import UserFactory
from apps.inputs.views import InputSupplyRequestViewSet, ShopkeeperPaymentHistoryViewSet
 
def build_escrow(unlock_pct=Decimal('100.00'), allowed=('seed',), cap_per_acre=Decimal('2000.00'),
    acres=Decimal('5.00'), approved=Decimal('100000.00')):
  loan = LoanApplicationFactory(approved_amount=approved, acres_applied_for=acres)
  CropLifecycleMilestoneFactory(crop=loan.crop, phase_number=1, unlock_pct=unlock_pct, allowed_input_categories=list(allowed))
  CropInputCapFactory(crop=loan.crop, district=loan.farmer.user.district, input_category = 'seed',
    valid_season=loan.crop.season, max_cost_per_acre=cap_per_acre)
  return EscrowCreationService.create(loan)
 
@pytest.mark.django_db
class TestProcessInputRequestGuardRails:
  def test_rejects_category_not_allowed_in_current_phase(self):
    escrow = build_escrow(allowed=('seed',))
    with pytest.raises(WrongPhaseForCategoryError):
      process_input_request(escrow.id, ShopkeeperProfileFactory(), 'fertilizer', Decimal('500.00'))
 
  def test_rejects_when_no_active_phase(self):
    escrow = build_escrow()
    escrow.unlocks.update(is_active=False)
    with pytest.raises(NoActivePhaseError):
      process_input_request(escrow.id, ShopkeeperProfileFactory(), 'seed', Decimal('500.00'))
 
  def test_rejects_when_no_afo_cap_record_exists_for_category(self):
    escrow = build_escrow(allowed=('seed', 'fertilizer'))
    with pytest.raises(AFOLimitExceededError):
      process_input_request(escrow.id, ShopkeeperProfileFactory(), 'fertilizer', Decimal('500.00'))
 
  def test_rejects_spending_beyond_the_afo_cap(self):
    escrow = build_escrow(cap_per_acre=Decimal('2000.00'), acres=Decimal('5.00'))
    with pytest.raises(AFOLimitExceededError):
      process_input_request(escrow.id, ShopkeeperProfileFactory(), 'seed', Decimal('10000.01'))
 
  def test_allows_spending_exactly_up_to_the_afo_cap(self):
    escrow = build_escrow(cap_per_acre=Decimal('2000.00'), acres=Decimal('5.00'))
    supply_request = process_input_request(escrow.id, ShopkeeperProfileFactory(), 'seed', Decimal('10000.00'))
    assert supply_request.requested_amount == Decimal('10000.00')
 
  def test_rejects_when_remaining_balance_is_the_binding_constraint(self):
    escrow = build_escrow(cap_per_acre=Decimal('50000.00'), acres=Decimal('5.00'))
    escrow.remaining_balance = Decimal('300.00')
    escrow.save(update_fields=['remaining_balance'])
    with pytest.raises(NotEnoughEscrowError):
      process_input_request(escrow.id, ShopkeeperProfileFactory(), 'seed', Decimal('301.00'))
 
@pytest.mark.django_db
class TestProcessInputRequestSuccessPath:
  def test_credits_shopkeeper_wallet_and_creates_a_paid_supply_request(self):
    escrow = build_escrow()
    shopkeeper = ShopkeeperProfileFactory()
    balance_before = shopkeeper.user.wallet.balance
    supply_request = process_input_request(escrow.id, shopkeeper, 'seed', Decimal('500.00'))
    assert supply_request.status == 'paid'
    shopkeeper.user.wallet.refresh_from_db()
    assert shopkeeper.user.wallet.balance == balance_before + Decimal('500.00')
 
  def test_decrements_escrow_balance_and_increments_total_spent_together(self):
    escrow = build_escrow()
    remaining_before = escrow.remaining_balance
    process_input_request(escrow.id, ShopkeeperProfileFactory(), 'seed', Decimal('500.00'))
    escrow.refresh_from_db()
    assert escrow.remaining_balance == remaining_before - Decimal('500.00')
    assert escrow.total_spent_on_inputs == Decimal('500.00')
 
@pytest.mark.django_db
class TestPhaseCapFixIsBypassedByThisDuplicatePath:
  def test_phase_cap_is_now_enforced_matching_escrow_s_behavior(self):
    escrow = build_escrow(unlock_pct=Decimal('10.00'), cap_per_acre=Decimal('5000.00'), acres=Decimal('5.00'))
    with pytest.raises(NotEnoughEscrowError):
      process_input_request(escrow.id, ShopkeeperProfileFactory(), 'seed', Decimal('10000.01'))
 
@pytest.mark.django_db
class TestAfoCapSnapshotInconsistencyAcrossEntryPoints:
  def test_snapshot_now_matches_escrow_s_pay_shopkeeper_for_identical_inputs(self):
    escrow = build_escrow(cap_per_acre=Decimal('2000.00'), acres=Decimal('5.00'))
    shopkeeper = ShopkeeperProfileFactory()
    InputPaymentService.process_payment(escrow.id, shopkeeper.user, 'seed', Decimal('100.00'))
    process_input_request(escrow.id, shopkeeper, 'seed', Decimal('100.00'))
    snapshots = set(escrow.transactions.filter(txn_type='input').values_list('afo_cap_snapshot', flat=True))
    assert snapshots == {Decimal('2000.00')}
 
  def test_afo_cap_ceiling_itself_is_at_least_correctly_shared_between_both_paths(self):
    escrow = build_escrow(cap_per_acre=Decimal('1000.00'), acres=Decimal('1.00'))
    shopkeeper = ShopkeeperProfileFactory()
    InputPaymentService.process_payment(escrow.id, shopkeeper.user, 'seed', Decimal('700.00'))
    with pytest.raises(AFOLimitExceededError):
      process_input_request(escrow.id, shopkeeper, 'seed', Decimal('400.00'))
 
@pytest.mark.django_db
class TestProcessInputRequestServiceLayerGaps:
  def test_negative_amount_is_now_rejected(self):
    escrow = build_escrow()
    with pytest.raises(ValueError):
      process_input_request(escrow.id, ShopkeeperProfileFactory(), 'seed', Decimal('-500.00'))
 
  def test_service_has_no_ownership_check_and_trusts_the_caller_entirely(self):
    escrow = build_escrow()
    supply_request = process_input_request(escrow.id, ShopkeeperProfileFactory(), 'seed', Decimal('50.00'))
    assert supply_request.status == 'paid'
 
  def test_shopkeeper_without_a_wallet_now_gets_one_created_on_demand(self):
    escrow = build_escrow()
    with mute_signals(post_save):
      shopkeeper_user = UserFactory(role = 'shopkeeper')
    shopkeeper = ShopkeeperProfile.objects.create(user=shopkeeper_user, shop_name = 'No Wallet Shop')
    supply_request = process_input_request(escrow.id, shopkeeper, 'seed', Decimal('100.00'))
    assert supply_request.status == 'paid'
    assert Wallet.objects.filter(user=shopkeeper_user).exists()

 
def build_escrow(unlock_pct=Decimal('100.00'), allowed=('seed',), cap_per_acre=Decimal('2000.00'), acres=Decimal('5.00')):
  loan = LoanApplicationFactory(approved_amount=Decimal('100000.00'), acres_applied_for=acres)
  CropLifecycleMilestoneFactory(crop=loan.crop, phase_number=1, unlock_pct=unlock_pct, allowed_input_categories=list(allowed))
  CropInputCapFactory(crop=loan.crop, district=loan.farmer.user.district, input_category = 'seed',
    valid_season=loan.crop.season, max_cost_per_acre=cap_per_acre)
  return EscrowCreationService.create(loan)
 
def make_escrow(loan=None, amount=Decimal('50000.00')):
  loan = loan or LoanApplicationFactory()
  return EscrowWallet.objects.create(loan=loan, total_funded=amount, remaining_balance=amount)
 
def make_supply_request(escrow, shopkeeper, input_category = 'seed', amount=Decimal('500.00'), status = 'paid'):
  return InputSupplyRequest.objects.create(escrow=escrow, shopkeeper=shopkeeper, input_category=input_category,
    requested_amount=amount, status=status)
 
@pytest.mark.django_db
class TestCreateEndpoint:
  def test_non_farmer_role_cannot_create(self):
    escrow = build_escrow()
    req = APIRequestFactory().post('/inputs/requests/', {'escrow_id': str(escrow.id), 'shopkeeper_id': str(ShopkeeperProfileFactory().user.id),
      'input_category': 'seed', 'amount': '100.00'})
    force_authenticate(req, user=UserFactory(role = 'shopkeeper'))
    assert InputSupplyRequestViewSet.as_view({'post': 'create'})(req).status_code == 403
 
  def test_farmer_can_pay_shopkeeper_successfully(self):
    escrow = build_escrow()
    shopkeeper = ShopkeeperProfileFactory()
    req = APIRequestFactory().post('/inputs/requests/', {'escrow_id': str(escrow.id), 'shopkeeper_id': str(shopkeeper.user.id),
      'input_category': 'seed', 'amount': '500.00'})
    force_authenticate(req, user=escrow.loan.farmer.user)
    response = InputSupplyRequestViewSet.as_view({'post': 'create'})(req)
    assert response.status_code == 201
    shopkeeper.user.wallet.refresh_from_db()
    assert shopkeeper.user.wallet.balance == Decimal('500.00')
 
  def test_rejects_when_escrow_does_not_belong_to_the_caller(self):
    escrow = build_escrow()
    shopkeeper = ShopkeeperProfileFactory()
    other_farmer = UserFactory(role = 'smallholder')
    req = APIRequestFactory().post('/inputs/requests/', {'escrow_id': str(escrow.id), 'shopkeeper_id': str(shopkeeper.user.id),
      'input_category': 'seed', 'amount': '100.00'})
    force_authenticate(req, user=other_farmer)
    assert InputSupplyRequestViewSet.as_view({'post': 'create'})(req).status_code == 403
 
  def test_nonexistent_escrow_returns_404(self):
    import uuid
    farmer = UserFactory(role = 'smallholder')
    req = APIRequestFactory().post('/inputs/requests/', {'escrow_id': str(uuid.uuid4()), 'shopkeeper_id': str(ShopkeeperProfileFactory().user.id),
      'input_category': 'seed', 'amount': '100.00'})
    force_authenticate(req, user=farmer)
    assert InputSupplyRequestViewSet.as_view({'post': 'create'})(req).status_code == 404
 
  def test_nonexistent_shopkeeper_returns_404(self):
    import uuid
    escrow = build_escrow()
    req = APIRequestFactory().post('/inputs/requests/', {'escrow_id': str(escrow.id), 'shopkeeper_id': str(uuid.uuid4()),
      'input_category': 'seed', 'amount': '100.00'})
    force_authenticate(req, user=escrow.loan.farmer.user)
    assert InputSupplyRequestViewSet.as_view({'post': 'create'})(req).status_code == 404
 
  def test_amount_below_minimum_is_blocked_by_min_value_not_the_custom_validator(self):
    escrow = build_escrow()
    req = APIRequestFactory().post('/inputs/requests/', {'escrow_id': str(escrow.id), 'shopkeeper_id': str(ShopkeeperProfileFactory().user.id),
      'input_category': 'seed', 'amount': '0.50'})
    force_authenticate(req, user=escrow.loan.farmer.user)
    response = InputSupplyRequestViewSet.as_view({'post': 'create'})(req)
    assert response.status_code == 400
    assert 'the amount s/h be > than zero.' not in str(response.data), ("validate_amount is dead code -- min_value=1.00 always fires first")
 
  def test_amount_of_exactly_the_minimum_is_accepted(self):
    escrow = build_escrow()
    req = APIRequestFactory().post('/inputs/requests/', {'escrow_id': str(escrow.id), 'shopkeeper_id': str(ShopkeeperProfileFactory().user.id),
      'input_category': 'seed', 'amount': '1.00'})
    force_authenticate(req, user=escrow.loan.farmer.user)
    assert InputSupplyRequestViewSet.as_view({'post': 'create'})(req).status_code == 201
 
  def test_invalid_input_category_choice_returns_400(self):
    escrow = build_escrow()
    req = APIRequestFactory().post('/inputs/requests/', {'escrow_id': str(escrow.id), 'shopkeeper_id': str(ShopkeeperProfileFactory().user.id),
      'input_category': 'diesel', 'amount': '100.00'})
    force_authenticate(req, user=escrow.loan.farmer.user)
    assert InputSupplyRequestViewSet.as_view({'post': 'create'})(req).status_code == 400
 
@pytest.mark.django_db
class TestListResponseShape:
  def test_list_returns_a_bare_array_not_the_standard_paginated_shape(self):
    escrow = make_escrow()
    make_supply_request(escrow, ShopkeeperProfileFactory())
    req = APIRequestFactory().get('/inputs/requests/')
    force_authenticate(req, user=escrow.loan.farmer.user)
    response = InputSupplyRequestViewSet.as_view({'get': 'list'})(req)
    assert isinstance(response.data, list), f"expected a bare list, got {type(response.data)}"
 
@pytest.mark.django_db
class TestListScoping:
  def test_farmer_sees_only_their_own_requests(self):
    escrow_a, escrow_b = make_escrow(), make_escrow()
    shopkeeper = ShopkeeperProfileFactory()
    mine = make_supply_request(escrow_a, shopkeeper)
    make_supply_request(escrow_b, shopkeeper)
    req = APIRequestFactory().get('/inputs/requests/')
    force_authenticate(req, user=escrow_a.loan.farmer.user)
    response = InputSupplyRequestViewSet.as_view({'get': 'list'})(req)
    assert {row['id'] for row in response.data} == {str(mine.id)}
 
  def test_shopkeeper_sees_only_requests_addressed_to_them(self):
    escrow = make_escrow()
    my_shopkeeper, other_shopkeeper = ShopkeeperProfileFactory(), ShopkeeperProfileFactory()
    mine = make_supply_request(escrow, my_shopkeeper)
    make_supply_request(escrow, other_shopkeeper)
    req = APIRequestFactory().get('/inputs/requests/')
    force_authenticate(req, user=my_shopkeeper.user)
    response = InputSupplyRequestViewSet.as_view({'get': 'list'})(req)
    assert {row['id'] for row in response.data} == {str(mine.id)}
 
  def test_bank_now_sees_only_requests_tied_to_their_own_bank(self):
    bank_a_user, bank_b_user = UserFactory(role='bank'), UserFactory(role='bank')
    escrow_a = make_escrow(loan=LoanApplicationFactory(bank=bank_a_user.bank_profile))
    escrow_b = make_escrow(loan=LoanApplicationFactory(bank=bank_b_user.bank_profile))
    shopkeeper = ShopkeeperProfileFactory()
    req_a = make_supply_request(escrow_a, shopkeeper)
    make_supply_request(escrow_b, shopkeeper)
    req = APIRequestFactory().get('/inputs/requests/')
    force_authenticate(req, user=bank_a_user)
    response = InputSupplyRequestViewSet.as_view({'get': 'list'})(req)
    assert {row['id'] for row in response.data} == {str(req_a.id)}
 
  def test_unrelated_role_is_forbidden_from_listing(self):
    escrow = make_escrow()
    make_supply_request(escrow, ShopkeeperProfileFactory())
    req = APIRequestFactory().get('/inputs/requests/')
    force_authenticate(req, user=UserFactory(role = 'landowner'))
    response = InputSupplyRequestViewSet.as_view({'get': 'list'})(req)
    assert response.status_code == 403
    assert response.data['detail'].code == 'permission_denied'
 
  def test_filters_by_input_category(self):
    escrow = make_escrow()
    shopkeeper = ShopkeeperProfileFactory()
    seed_req = make_supply_request(escrow, shopkeeper, input_category = 'seed')
    make_supply_request(escrow, shopkeeper, input_category = 'fertilizer')
    req = APIRequestFactory().get('/inputs/requests/', {'input_category': 'seed'})
    force_authenticate(req, user=escrow.loan.farmer.user)
    response = InputSupplyRequestViewSet.as_view({'get': 'list'})(req)
    assert {row['id'] for row in response.data} == {str(seed_req.id)}
 
  def test_filters_by_status(self):
    escrow = make_escrow()
    shopkeeper = ShopkeeperProfileFactory()
    paid = make_supply_request(escrow, shopkeeper, status = 'paid')
    make_supply_request(escrow, shopkeeper, status = 'pending')
    req = APIRequestFactory().get('/inputs/requests/', {'status': 'paid'})
    force_authenticate(req, user=escrow.loan.farmer.user)
    response = InputSupplyRequestViewSet.as_view({'get': 'list'})(req)
    assert {row['id'] for row in response.data} == {str(paid.id)}
 
@pytest.mark.django_db
class TestRetrieveDeadCodeCheck:
  def test_farmer_retrieving_their_own_request_succeeds(self):
    escrow = make_escrow()
    mine = make_supply_request(escrow, ShopkeeperProfileFactory())
    req = APIRequestFactory().get(f'/inputs/requests/{mine.id}/')
    force_authenticate(req, user=escrow.loan.farmer.user)
    response = InputSupplyRequestViewSet.as_view({'get': 'retrieve'})(req, pk=str(mine.id))
    assert response.status_code == 200
 
  def test_farmer_retrieving_someone_else_s_request_gets_404_not_403(self):
    other_escrow = make_escrow()
    theirs = make_supply_request(other_escrow, ShopkeeperProfileFactory())
    outsider = UserFactory(role = 'smallholder')
    req = APIRequestFactory().get(f'/inputs/requests/{theirs.id}/')
    force_authenticate(req, user=outsider)
    response = InputSupplyRequestViewSet.as_view({'get': 'retrieve'})(req, pk=str(theirs.id))
    assert response.status_code == 404, "dead code confirmed -- get_object() 404s before the manual 403 check ever runs"
 
  def test_shopkeeper_retrieving_someone_else_s_request_also_gets_404_not_403(self):
    escrow = make_escrow()
    theirs = make_supply_request(escrow, ShopkeeperProfileFactory())
    outsider_shopkeeper = ShopkeeperProfileFactory()
    req = APIRequestFactory().get(f'/inputs/requests/{theirs.id}/')
    force_authenticate(req, user=outsider_shopkeeper.user)
    response = InputSupplyRequestViewSet.as_view({'get': 'retrieve'})(req, pk=str(theirs.id))
    assert response.status_code == 404
 
@pytest.mark.django_db
class TestHttpMethodRestrictions:
  def test_patch_is_blocked_with_405(self):
    escrow = make_escrow()
    req_obj = make_supply_request(escrow, ShopkeeperProfileFactory())
    req = APIRequestFactory().patch(f'/inputs/requests/{req_obj.id}/', {'status': 'paid'})
    force_authenticate(req, user=escrow.loan.farmer.user)
    response = InputSupplyRequestViewSet.as_view({'patch': 'partial_update'})(req, pk=str(req_obj.id))
    assert response.status_code == 405
 
  def test_delete_is_blocked_with_405(self):
    escrow = make_escrow()
    req_obj = make_supply_request(escrow, ShopkeeperProfileFactory())
    req = APIRequestFactory().delete(f'/inputs/requests/{req_obj.id}/')
    force_authenticate(req, user=escrow.loan.farmer.user)
    response = InputSupplyRequestViewSet.as_view({'delete': 'destroy'})(req, pk=str(req_obj.id))
    assert response.status_code == 405
 
@pytest.mark.django_db
class TestShopkeeperPaymentHistory:
  def test_non_shopkeeper_role_is_blocked_entirely(self):
    req = APIRequestFactory().get('/inputs/shopkeeper-history/')
    force_authenticate(req, user=UserFactory(role = 'bank'))
    assert ShopkeeperPaymentHistoryViewSet.as_view({'get': 'list'})(req).status_code == 403
 
  def test_shows_only_this_shopkeeper_s_paid_requests(self):
    escrow = make_escrow()
    me, other = ShopkeeperProfileFactory(), ShopkeeperProfileFactory()
    mine = make_supply_request(escrow, me, status = 'paid')
    make_supply_request(escrow, other, status = 'paid')
    req = APIRequestFactory().get('/inputs/shopkeeper-history/')
    force_authenticate(req, user=me.user)
    response = ShopkeeperPaymentHistoryViewSet.as_view({'get': 'list'})(req)
    assert {row['id'] for row in response.data} == {str(mine.id)}
 
  def test_history_list_is_also_a_bare_array(self):
    escrow = make_escrow()
    shopkeeper = ShopkeeperProfileFactory()
    make_supply_request(escrow, shopkeeper, status = 'paid')
    req = APIRequestFactory().get('/inputs/shopkeeper-history/')
    force_authenticate(req, user=shopkeeper.user)
    response = ShopkeeperPaymentHistoryViewSet.as_view({'get': 'list'})(req)
    assert isinstance(response.data, list)
 
  def test_filters_by_input_category(self):
    escrow = make_escrow()
    shopkeeper = ShopkeeperProfileFactory()
    seed_req = make_supply_request(escrow, shopkeeper, input_category = 'seed', status = 'paid')
    make_supply_request(escrow, shopkeeper, input_category = 'fertilizer', status = 'paid')
    req = APIRequestFactory().get('/inputs/shopkeeper-history/', {'input_category': 'seed'})
    force_authenticate(req, user=shopkeeper.user)
    response = ShopkeeperPaymentHistoryViewSet.as_view({'get': 'list'})(req)
    assert {row['id'] for row in response.data} == {str(seed_req.id)}