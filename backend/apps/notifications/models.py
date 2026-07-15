from shared.models import BaseModel
from django.db import models

class Notification(BaseModel):
  EVENT_TYPES = (
    ('loan_approved', 'Loan Approved'),
    ('loan_rejected', 'Loan Rejected'),
    ('loan_disbursed', 'Loan Disbursed'),
    ('escrow_phase_unlocked', 'Escrow Phase Unlocked'),
    ('agreement_approved', 'Tenant Agreement Approved'),
    ('agreement_rejected', 'Tenant Agreement Rejected'),
    ('input_payment_success', 'Input Payment Successful'),
    ('payment_received', 'Payment Received'),
    ('settlement_complete', 'Settlement Complete'),
    ('factory_settlement_confirmed', 'Factory Settlement Confirmed'),
    ('claim_filed', 'Insurance Claim Filed'),
    ('claim_reviewed', 'Insurance Claim Reviewed'),
    ('verification_request_received', 'Verification Request Received'),
    ('numberdar_approved', 'Numberdar Approved'),   
    ('numberdar_rejected', 'Numberdar Rejected'),  
    ('verification_escalated', 'Verification Escalated'),
    ('credit_otp_sent', 'Credit OTP Sent'),  
    ('credit_check_completed', 'Credit Check Completed'),
    ('credit_check_manual_review', 'Credit Check Manual Review'),
    ('batch_received', 'Batch Received'),      
    ('delivery_confirmed', 'Delivery Confirmed'),
  )
  
  CHANNEL_CHOICES = (
    ('email', 'Email'),
    ('sms', 'SMS')
  )
  
  STATUS_CHOICES = (
    ('sent', 'Sent'),
    ('failed', 'Failed'),
    ('stubbed', 'Stubbed — SMS gateway pending')
  )
  recipient = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name = 'notifications')
  event_type = models.CharField(max_length=50, choices=EVENT_TYPES, db_index=True)
  channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
  subject = models.CharField(max_length=200, blank=True)
  message = models.TextField()
  reference_id = models.UUIDField(null=True, blank=True)
  status = models.CharField(max_length=30, choices=STATUS_CHOICES, default = 'stubbed', db_index=True)
  error_message = models.TextField(blank=True)
  is_read = models.BooleanField(default=False, db_index=True)
  sent_at = models.DateTimeField(null=True, blank=True)
  read_at = models.DateTimeField(null=True, blank=True)

  class Meta:
    db_table = 'notification_logs'
    ordering = ['-created_at']
    indexes = [models.Index(fields=['recipient', 'is_read']), models.Index(fields=['recipient', '-created_at'])]