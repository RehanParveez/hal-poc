import factory
from apps.wallets.models import Wallet, WalletTransaction
from apps.accounts.tests.factories import UserFactory
from decimal import Decimal

class WalletFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = Wallet
    django_get_or_create = ('user',)

  user = factory.SubFactory(UserFactory)
  wallet_type = 'farmer'
  balance = Decimal('0')

class WalletTransactionFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = WalletTransaction
  wallet = factory.SubFactory(WalletFactory)
  amount = Decimal('100.00')
  direction = 'credit'
  txn_type = 'profit'