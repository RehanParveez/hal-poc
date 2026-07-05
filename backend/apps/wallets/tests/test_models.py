import uuid
import pytest
from apps.accounts.tests.factories import UserFactory
from apps.wallets.tests.factories import WalletFactory, WalletTransactionFactory
from apps.wallets.models import Wallet, WalletTransaction
from django.db import IntegrityError
from decimal import Decimal
from django.db.models.deletion import ProtectedError

@pytest.mark.django_db
class TestWalletModelConstraints:
  def test_one_wallet_per_user_is_enforced_at_db_level(self):
    user = UserFactory()
    WalletFactory(user=user)
    with pytest.raises(IntegrityError):
      
      Wallet.objects.create(user=user, wallet_type='farmer', balance=Decimal('0'))
  def test_wallet_transaction_is_protected_from_wallet_deletion(self):
    wallet = WalletFactory()
    WalletTransactionFactory(wallet=wallet)
    with pytest.raises(ProtectedError):
      wallet.delete()

  def test_negative_balance_is_not_rejected_by_the_database(self):
    wallet = WalletFactory(balance=Decimal('50.00'))
    wallet.balance = Decimal('-999.00')
    wallet.save(update_fields=['balance'])
    wallet.refresh_from_db()
    assert wallet.balance == Decimal('-999.00')

@pytest.mark.django_db
class TestWalletTransactionModelConstraints:
  def test_duplicate_reference_id_on_same_wallet_is_allowed(self):
    wallet = WalletFactory()
    ref = uuid.uuid4()
    WalletTransactionFactory(wallet=wallet, reference_id=ref, txn_type='settlement')
    WalletTransactionFactory(wallet=wallet, reference_id=ref, txn_type='settlement')
    assert WalletTransaction.objects.filter(wallet=wallet, reference_id=ref).count() == 2