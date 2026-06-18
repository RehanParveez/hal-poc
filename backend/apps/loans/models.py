from django.db import models
from shared.models import BaseModel

class LoanApplication(BaseModel):
  STATUS_CHOICES = (
    ('submitted', 'Submitted'),
    ('bank_approved', 'Bank Approved'),
    ('disbursed', 'Disbursed'),
    ('repaid', 'Fully Repaid'),
    ('rejected', 'Rejected'),
  )
  farmer = models.ForeignKey('accounts.FarmerProfile', on_delete=models.PROTECT, related_name = 'loan_applications')
  bank = models.ForeignKey('accounts.BankProfile', on_delete=models.PROTECT, related_name = 'loan_applications')
  tenant_agreement = models.ForeignKey('land.TenantAgreement', on_delete=models.PROTECT, related_name = 'loan_applications',
    null=True, blank=True)
  crop = models.ForeignKey('crops.CropType', on_delete=models.PROTECT, related_name = 'loan_applications')
  acres_applied_for = models.DecimalField(max_digits=10, decimal_places=2)
  requested_amount = models.DecimalField(max_digits=12, decimal_places=2)
  approved_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
  interest_rate_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
  status = models.CharField(max_length=30, choices=STATUS_CHOICES, default = 'submitted')
  rejection_reason = models.TextField(blank=True)
  loan_recovered_to_date = models.DecimalField(max_digits=14, decimal_places=2, default=0)
  approved_at = models.DateTimeField(null=True, blank=True)
  disbursed_at = models.DateTimeField(null=True, blank=True)

  class Meta:
    db_table = 'loan_applications'
    indexes = [models.Index(fields=['farmer', 'status']), models.Index(fields=['bank', 'status']), models.Index(fields=['status'])]

  def __str__(self):
    return f"{self.farmer.user.full_name}"