from django.db import models
from shared.models import BaseModel

class EscrowWallet(BaseModel):
  loan = models.OneToOneField('loans.LoanApplication', on_delete=models.PROTECT, related_name = 'escrow')
  total_funded = models.DecimalField(max_digits=14, decimal_places=2)
  insurance_premium_deducted = models.DecimalField(max_digits=14, decimal_places=2, default=0)
  total_spent_on_inputs = models.DecimalField(max_digits=14, decimal_places=2, default=0)
  remaining_balance = models.DecimalField(max_digits=14, decimal_places=2)

  class Meta:
    db_table = 'escrow_wallets'

  def __str__(self):
    return f"escrow({self.loan.farmer.user.full_name})"

  @property
  def project_district(self):
    if self.loan.tenant_agreement and self.loan.tenant_agreement.parcel:
      return self.loan.tenant_agreement.parcel.district
    return self.loan.farmer.user.district

  @property
  def active_unlock(self):
    return self.unlocks.filter(is_active=True).select_related('milestone').first()

  @property
  def loan_crop_code(self):
    return self.loan.crop.code

  @property
  def loan_acres(self):
    return self.loan.acres_applied_for

  @property
  def loan_season(self):
    return self.loan.crop.season

class EscrowMilestoneUnlock(BaseModel):
  escrow = models.ForeignKey(EscrowWallet, on_delete=models.CASCADE, related_name = 'unlocks')
  milestone = models.ForeignKey('crops.CropLifecycleMilestone', on_delete=models.PROTECT)
  unlocked_amount = models.DecimalField(max_digits=12, decimal_places=2)
  unlocked_at = models.DateTimeField(null=True, blank=True)
  is_active = models.BooleanField(default=False, db_index=True)

  class Meta:
    db_table = 'escrow_milestone_unlocks'
    unique_together = [['escrow', 'milestone']]

  def __str__(self):
    state = 'ACTIVE' if self.is_active else 'done'
    return f"Phase {self.milestone.phase_number} ({self.milestone.phase_name}) [{state}]"

class EscrowTransaction(BaseModel):
  TXN_TYPES = (
    ('insurance', 'Insurance'),
    ('input', 'Input')
  )
  escrow = models.ForeignKey(EscrowWallet, on_delete=models.PROTECT, related_name = 'transactions')
  txn_type = models.CharField(max_length=30, choices=TXN_TYPES)
  amount = models.DecimalField(max_digits=12, decimal_places=2)
  recipient = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name = 'received_escrow_transactions')
  input_category = models.CharField(max_length=30, blank=True)
  afo_cap_snapshot = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

  class Meta:
    db_table = 'escrow_transactions'
    ordering = ['-created_at']
    indexes = [models.Index(fields=['escrow', 'txn_type']), models.Index(fields=['escrow', 'input_category'])]

  def __str__(self):
    return f"{self.txn_type}"