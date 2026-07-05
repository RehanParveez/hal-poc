import pytest
from factory.django import mute_signals
from django.db.models.signals import post_save
from apps.accounts.tests.factories import UserFactory
from apps.wallets.models import Wallet, WalletTransaction
from decimal import Decimal
from apps.wallets.services import WalletService
from apps.wallets.tests.factories import WalletFactory, WalletTransactionFactory
import uuid
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.wallets.views import WalletViewSet, WalletTransactionViewSet
from apps.wallets.serializers.detail import WalletSerializer
from apps.wallets.serializers.basic import WalletSerializer1

@pytest.mark.django_db
class TestCreateWalletForUser:
  def test_creates_a_new_wallet_when_none_exists(self):
    with mute_signals(post_save):
      user = UserFactory(role = 'smallholder')
    wallet, created = WalletService.create_wallet_for_user(user, wallet_type = 'farmer')
    assert created is True
    assert wallet.user == user
    assert wallet.wallet_type == 'farmer'
    assert wallet.balance == Decimal('0')

  def test_returns_existing_wallet_without_creating_a_duplicate(self):
    user = UserFactory(role = 'smallholder')
    first, _ = WalletService.create_wallet_for_user(user, wallet_type = 'farmer')
    second, created = WalletService.create_wallet_for_user(user, wallet_type = 'farmer')
    assert created is False
    assert second.id == first.id
    assert Wallet.objects.filter(user=user).count() == 1

  def test_mismatched_wallet_type_on_an_existing_wallet_is_silently_ignored(self):
    user = UserFactory(role = 'smallholder')
    WalletService.create_wallet_for_user(user, wallet_type = 'farmer')
    wallet, created = WalletService.create_wallet_for_user(user, wallet_type = 'landowner')
    assert created is False
    assert wallet.wallet_type == 'farmer'

@pytest.mark.django_db
class TestGetOrCreatePlatformWallet:
  def test_creates_platform_wallet_using_the_admin_user(self):
    admin = UserFactory(role='admin')
    wallet, created = WalletService.get_or_create_platform_wallet()
    assert created is True
    assert wallet.wallet_type == 'platform'
    assert wallet.user == admin

  def test_returns_existing_platform_wallet_on_second_call(self):
    UserFactory(role='admin')
    first, _ = WalletService.get_or_create_platform_wallet()
    second, created = WalletService.get_or_create_platform_wallet()
    assert created is False
    assert second.id == first.id
    assert Wallet.objects.filter(wallet_type = 'platform').count() == 1

  def test_raises_value_error_when_no_admin_user_exists(self):
    with pytest.raises(ValueError):
      WalletService.get_or_create_platform_wallet()

@pytest.mark.django_db
class TestCreditWallet:
  def test_credit_increases_balance_by_exact_amount(self):
    wallet = WalletFactory()
    wallet.balance = Decimal('100.00')
    wallet.save()
    updated = WalletService.credit_wallet(wallet, amount=Decimal('50.00'), txn_type = 'profit')
    assert updated.balance == Decimal('150.00')

  def test_credit_writes_a_transaction_row_with_correct_fields(self):
    wallet = WalletFactory() 
    WalletService.credit_wallet(wallet, amount=Decimal('25.00'), txn_type = 'profit', note = 'harvest payout')
    txn = WalletTransaction.objects.get(wallet=wallet)
    assert txn.amount == Decimal('25.00')
    assert txn.direction == 'credit'
    assert txn.txn_type == 'profit'
    assert txn.note == 'harvest payout'

  def test_repeated_fractional_credits_accumulate_exactly(self):
    wallet = WalletFactory() 
    for _ in range(3):
      WalletService.credit_wallet(wallet, amount=Decimal('0.10'), txn_type = 'profit')
    wallet.refresh_from_db()
    assert wallet.balance == Decimal('0.30')

  def test_credit_with_a_negative_amount_still_mutates_the_balance(self):
    wallet = WalletFactory()
    wallet.balance = Decimal('100.00')
    wallet.save()
    WalletService.credit_wallet(wallet, amount=Decimal('-40.00'), txn_type = 'profit')
    wallet.refresh_from_db()
    assert wallet.balance == Decimal('60.00')

@pytest.mark.django_db
class TestDebitWallet:
  def test_debit_decreases_balance_by_exact_amount(self):
    wallet = WalletFactory()
    wallet.balance = Decimal('100.00')
    wallet.save()
    updated = WalletService.debit_wallet(wallet, amount=Decimal('30.00'), txn_type = 'fee')
    assert updated.balance == Decimal('70.00')

  def test_debit_of_exactly_the_full_balance_succeeds_and_zeroes_it_out(self):
    wallet = WalletFactory()
    wallet.balance = Decimal('40.00')
    wallet.save()  
    updated = WalletService.debit_wallet(wallet, amount=Decimal('40.00'), txn_type = 'fee')
    assert updated.balance == Decimal('0.00')

  def test_debit_of_one_paisa_more_than_balance_is_rejected(self):
    wallet = WalletFactory()
    wallet.balance = Decimal('40.00')
    wallet.save()
    with pytest.raises(ValueError):
      WalletService.debit_wallet(wallet, amount=Decimal('40.01'), txn_type = 'fee')

  def test_rejected_debit_leaves_balance_and_ledger_untouched(self):
    wallet = WalletFactory()
    wallet.balance = Decimal('40.00')
    wallet.save()
    with pytest.raises(ValueError):
      WalletService.debit_wallet(wallet, amount=Decimal('999.00'), txn_type = 'fee')
    wallet.refresh_from_db()
    assert wallet.balance == Decimal('40.00')
    assert WalletTransaction.objects.filter(wallet=wallet).count() == 0

  def test_debit_with_a_negative_amount_still_increases_the_balance(self):
    wallet = WalletFactory()
    wallet.balance = Decimal('100.00')
    wallet.save()
    WalletService.debit_wallet(wallet, amount=Decimal('-40.00'), txn_type = 'fee')
    wallet.refresh_from_db()
    assert wallet.balance == Decimal('140.00')

  def test_repeated_calls_with_the_same_reference_id_double_process(self):
    wallet = WalletFactory()
    wallet.balance = Decimal('200.00')
    wallet.save()
    ref = uuid.uuid4()
    WalletService.debit_wallet(wallet, amount=Decimal('50.00'), txn_type = 'fee', reference_id=ref)
    WalletService.debit_wallet(wallet, amount=Decimal('50.00'), txn_type = 'fee', reference_id=ref)
    wallet.refresh_from_db()
    assert wallet.balance == Decimal('100.00')
    assert WalletTransaction.objects.filter(wallet=wallet, reference_id=ref).count() == 2
    
@pytest.mark.django_db
class TestWalletViewSetAccessControl:
  def test_list_requires_authentication(self):
    factory = APIRequestFactory()
    request = factory.get('/wallets/')
    view = WalletViewSet.as_view({'get': 'list'})
    response = view(request)
    assert response.status_code == 401

  def test_list_returns_only_own_wallet_for_regular_user_but_all_wallets_for_admin(self):
    viewer = UserFactory(role = 'smallholder')
    other = UserFactory(role = 'smallholder')
    admin = UserFactory(role = 'admin')
    viewer_wallet = WalletFactory(user=viewer)
    other_wallet = WalletFactory(user=other)

    factory = APIRequestFactory()

    request = factory.get('/wallets/')
    force_authenticate(request, user=viewer)
    response = WalletViewSet.as_view({'get': 'list'})(request)
    assert {str(r['id']) for r in response.data['results']} == {str(viewer_wallet.id)}
    request = factory.get('/wallets/')
    force_authenticate(request, user=admin)
    response = WalletViewSet.as_view({'get': 'list'})(request)
    seen = {str(r['id']) for r in response.data['results']}
    assert seen == {str(viewer_wallet.id), str(other_wallet.id)}

  def test_my_balance_returns_the_caller_s_own_wallet(self):
    user = UserFactory(role = 'smallholder')
    wallet = WalletFactory(user=user)
    wallet.balance = Decimal('321.50')
    wallet.save() 
    
    factory = APIRequestFactory()
    request = factory.get('/wallets/my_balance/')
    force_authenticate(request, user=user)
    view = WalletViewSet.as_view({'get': 'my_balance'})
    response = view(request)
    assert response.status_code == 200
    assert response.data['id'] == str(wallet.id)
    assert Decimal(response.data['balance']) == Decimal('321.50')

  def test_my_balance_returns_404_when_user_has_no_wallet(self):
    with mute_signals(post_save):
      user = UserFactory(role='smallholder')
      
    factory = APIRequestFactory()
    request = factory.get('/wallets/my_balance/')
    force_authenticate(request, user=user)
    view = WalletViewSet.as_view({'get': 'my_balance'})
    response = view(request)
    assert response.status_code == 404

  def test_get_serializer_class_returns_different_serializers_for_list_and_retrieve(self):
    view = WalletViewSet()
    view.action = 'list'
    list_serializer = view.get_serializer_class()
    view.action = 'retrieve'
    retrieve_serializer = view.get_serializer_class()
    assert list_serializer is WalletSerializer1
    assert retrieve_serializer is WalletSerializer
    assert list_serializer is not retrieve_serializer

  def test_list_only_returns_the_caller_s_own_transactions(self):
    viewer = UserFactory(role = 'smallholder')
    other = UserFactory(role = 'smallholder')
    viewer_wallet = WalletFactory(user=viewer)
    other_wallet = WalletFactory(user=other)
    WalletTransactionFactory(wallet=viewer_wallet, txn_type = 'profit')
    WalletTransactionFactory(wallet=other_wallet, txn_type = 'profit')

    factory = APIRequestFactory()
    request = factory.get('/wallet-transactions/')
    force_authenticate(request, user=viewer)
    view = WalletTransactionViewSet.as_view({'get': 'list'})
    response = view(request)
    wallets_seen = {str(row['wallet']) for row in response.data['results']}
    assert wallets_seen == {str(viewer_wallet.id)}

  def test_txn_type_query_param_filters_results(self):
    user = UserFactory(role='smallholder')
    wallet = WalletFactory(user=user)
    WalletTransactionFactory(wallet=wallet, txn_type = 'profit', direction = 'credit')
    WalletTransactionFactory(wallet=wallet, txn_type = 'fee', direction = 'debit')

    factory = APIRequestFactory()
    request = factory.get('/wallet-transactions/', {'txn_type': 'fee'})
    force_authenticate(request, user=user)
    view = WalletTransactionViewSet.as_view({'get': 'list'})
    response = view(request)
    txn_types = {row['txn_type'] for row in response.data['results']}
    assert txn_types == {'fee'}

  def test_direction_query_param_filters_results(self):
    user = UserFactory(role = 'smallholder')
    wallet = WalletFactory(user=user)
    WalletTransactionFactory(wallet=wallet, txn_type='profit', direction = 'credit')
    WalletTransactionFactory(wallet=wallet, txn_type='fee', direction = 'debit')

    factory = APIRequestFactory()
    request = factory.get('/wallet-transactions/', {'direction': 'debit'})
    force_authenticate(request, user=user)
    view = WalletTransactionViewSet.as_view({'get': 'list'})
    response = view(request)
    directions = {row['direction'] for row in response.data['results']}
    assert directions == {'debit'}

  def test_results_are_ordered_newest_first(self):
    user = UserFactory(role='smallholder')
    wallet = WalletFactory(user=user)
    first = WalletTransactionFactory(wallet=wallet, txn_type = 'profit')
    second = WalletTransactionFactory(wallet=wallet, txn_type = 'fee')

    factory = APIRequestFactory()
    request = factory.get('/wallet-transactions/')
    force_authenticate(request, user=user)
    view = WalletTransactionViewSet.as_view({'get': 'list'})
    response = view(request)
    ids_in_order = [row['id'] for row in response.data['results']]
    assert ids_in_order == [str(second.id), str(first.id)]