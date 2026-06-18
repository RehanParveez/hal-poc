from django.db import models
from shared.models import BaseModel

class InsurancePolicy(BaseModel):
  STATUS_CHOICES = (
    ('active', 'Active'),
    ('claimed', 'Claimed'),
    ('expired', 'Expired'),
  )
  loan = models.OneToOneField('loans.LoanApplication', on_delete=models.PROTECT, related_name = 'insurance_policy')
  insurer = models.ForeignKey('accounts.InsuranceProfile', on_delete=models.PROTECT, related_name = 'policies', null=True, blank=True)
  coverage_amount = models.DecimalField(max_digits=14, decimal_places=2)
  premium_amount = models.DecimalField(max_digits=14, decimal_places=2)
  status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='active', db_index=True)
  policy_start = models.DateField()
  policy_end = models.DateField()

  class Meta:
    db_table = 'insurance_policies'
    indexes = [models.Index(fields=['status'])]

  def __str__(self):
    return f"policy({self.loan.farmer.user.full_name})"

class InsuranceClaim(BaseModel):
  STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
  )
  policy = models.ForeignKey(InsurancePolicy, on_delete=models.PROTECT, related_name='claims')
  claimed_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='insurance_claims')
  reason = models.TextField()
  claim_amount = models.DecimalField(max_digits=14, decimal_places=2)
  approved_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
  reviewer_note = models.TextField(blank=True)
  resolved_at = models.DateTimeField(null=True, blank=True)

  class Meta:
    db_table = 'insurance_claims'
    indexes = [models.Index(fields=['policy', 'status']), models.Index(fields=['claimed_by', 'status'])]

  def __str__(self):
    return f"claim({self.policy.loan.farmer.user.full_name})"