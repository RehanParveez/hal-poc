from django.db import models
from shared.models import BaseModel

class OTPConsent(BaseModel):
  PURPOSE_CHOICES = (('credit_check', 'Credit Check'),)

  user = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name = 'otp_consents')
  purpose = models.CharField(max_length=40, choices=PURPOSE_CHOICES, default = 'credit_check')
  phone_sent_to = models.CharField(max_length=35)
  otp_hash = models.CharField(max_length=125)
  verified = models.BooleanField(default=False)
  verified_at = models.DateTimeField(null=True, blank=True)
  expires_at = models.DateTimeField()

  class Meta:
    db_table = 'otp_consents'
    indexes = [models.Index(fields=['user', 'purpose', 'verified'])]

  def __str__(self):
    return f'otp{self.user.phone}'


class CreditCheck(BaseModel):
  STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
    ('manual_review', 'Manual Review')
  )
  
  RISK_TIER_CHOICES = (
    ('low_risk', 'Low Risk'),
    ('medium_risk', 'Medium Risk'),
    ('high_risk', 'High Risk'),
    ('unverified', 'Unverified')
  )
  
  ECIB_STATUS_CHOICES = (
    ('regular', 'Regular'),
    ('overdue', 'Overdue'),
    ('write_off', 'Write-Off'),
    ('none', 'None')
  )

  farmer = models.ForeignKey('accounts.FarmerProfile', on_delete=models.PROTECT, related_name = 'credit_checks')
  loan_application = models.ForeignKey('loans.LoanApplication', on_delete=models.PROTECT, related_name = 'credit_checks', null=True, blank=True)
  cnic_number = models.CharField(max_length=25)
  status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending', db_index=True)
  risk_tier = models.CharField(max_length=25, choices=RISK_TIER_CHOICES, null=True, blank=True)
  credit_score = models.PositiveSmallIntegerField(null=True, blank=True)
  total_outstanding_debt = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
  default_history_flag = models.BooleanField(default=False)
  active_micro_loans_count = models.PositiveSmallIntegerField(null=True, blank=True)
  ecib_status = models.CharField(max_length=25, choices=ECIB_STATUS_CHOICES, null=True, blank=True)
  max_approved_limit_pkr = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
  is_eligible = models.BooleanField(null=True, blank=True)
  bank_reference_id = models.CharField(max_length=120, blank=True)
  bank_decision_notes = models.TextField(blank=True)
  consent_timestamp = models.DateTimeField(null=True, blank=True)
  otp_reference = models.UUIDField(null=True, blank=True)
  raw_bank_response = models.JSONField(null=True, blank=True)
  request_payload_hash = models.CharField(max_length=68, blank=True)
  requested_at = models.DateTimeField(auto_now_add=True)
  completed_at = models.DateTimeField(null=True, blank=True)

  class Meta:
    db_table = 'credit_checks'
    indexes = [models.Index(fields=['farmer', 'status']), models.Index(fields=['loan_application']), models.Index(fields=['requested_at'])]

  def __str__(self):
    return f'creditCheck({self.farmer.user.full_name})'