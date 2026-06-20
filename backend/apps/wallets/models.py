from shared.models import BaseModel
from django.db import models

class Wallet(BaseModel):
  WALLET_TYPES = (
    ('farmer', 'Farmer'),
    ('landowner', 'Landowner'),
    ('shopkeeper', 'Shopkeeper'),
    ('platform', 'Platform'),
    ('bank', 'Bank'),
    ('bank_clearing', 'Bank Clearing'),
  )
  user = models.OneToOneField('accounts.User', on_delete=models.PROTECT, related_name = 'wallet')
  wallet_type = models.CharField(max_length=25, choices=WALLET_TYPES, db_index=True)
  balance = models.DecimalField(max_digits=16, decimal_places=2, default=0)

  class Meta:
    db_table = 'wallets'
    indexes = [models.Index(fields=['wallet_type'])]

  def __str__(self):
    return f"{self.wallet_type}"

class WalletTransaction(BaseModel):
  TXN_TYPES = (
    ('input', 'Input'),
    ('profit', 'Profit'),
    ('fee', 'Fee'),
    ('theka', 'Theka'),
    ('batai', 'Batai'),
    ('insurance', 'Insurance'),
    ('settlement', 'Settlement'),
  )
  wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name = 'transactions')
  amount = models.DecimalField(max_digits=14, decimal_places=2)
  direction = models.CharField(max_length=6, choices=[('debit', 'Debit'), ('credit', 'Credit')])
  txn_type = models.CharField(max_length=30, choices=TXN_TYPES, db_index=True)
  reference_id = models.UUIDField(null=True, blank=True)
  note = models.TextField(blank=True)

  class Meta:
    db_table = 'wallet_transactions'
    indexes = [models.Index(fields=['wallet', '-created_at']), models.Index(fields=['txn_type'])]

  def __str__(self):
    return f"{self.direction}"