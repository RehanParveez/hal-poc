from django.db import transaction
from apps.wallets.models import Wallet
from decimal import Decimal
from apps.accounts.models import User
from apps.wallets.models import WalletTransaction

class WalletService:
  @staticmethod
  def create_wallet_for_user(user, wallet_type):
    with transaction.atomic():
      wallet, created = Wallet.objects.get_or_create(user=user, defaults={'wallet_type': wallet_type, 'balance': Decimal('0')})
      return wallet, created

  @staticmethod
  def get_or_create_platform_wallet():
    with transaction.atomic():
      platform_wallet = Wallet.objects.filter(wallet_type='platform').first()
      if platform_wallet:
        return platform_wallet, False
      platform_admin = User.objects.filter(role='admin').first()
      if not platform_admin:
        raise ValueError("no platform_admin user exists. first create one before seeding the platf wallet.")
      wallet = Wallet.objects.create(user=platform_admin, wallet_type = 'platform', balance=Decimal('0'))
      return wallet, True

  @staticmethod
  def credit_wallet(wallet, amount, txn_type, reference_id=None, note=''):
    with transaction.atomic():
      wallet_locked = type(wallet).objects.select_for_update().get(id=wallet.id)
      wallet_locked.balance += amount
      wallet_locked.save(update_fields=['balance'])
      WalletTransaction.objects.create(wallet=wallet_locked, amount=amount, direction='credit', txn_type=txn_type, reference_id=reference_id, note=note)
      return wallet_locked

  @staticmethod
  def debit_wallet(wallet, amount, txn_type, reference_id=None, note=''):
    with transaction.atomic():
      wallet_locked = type(wallet).objects.select_for_update().get(id=wallet.id)
      if amount > wallet_locked.balance:
        raise ValueError(f"not enough wallet balance. Available: PKR {wallet_locked.balance}, requested: PKR {amount}.")
      wallet_locked.balance -= amount
      wallet_locked.save(update_fields=['balance'])
      WalletTransaction.objects.create(wallet=wallet_locked, amount=amount, direction='debit', txn_type=txn_type,
        reference_id=reference_id, note=note)
      return wallet_locked