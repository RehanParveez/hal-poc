from shared.models import BaseModel
from django.db import models
from django.contrib.postgres.fields import ArrayField

class NumberdarProfile(BaseModel):
  user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name = 'numberdar_profile')
  jurisdiction_district = models.CharField(max_length=130, blank=True, default='', db_index=True)
  jurisdiction_villages = ArrayField(models.CharField(max_length=120), blank=True, default=list)
  cnic_verified = models.BooleanField(default=False)
  authorized_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name = 'numberdars_authorized')
  authorized_at = models.DateTimeField(null=True, blank=True)
  total_farmers_verified = models.PositiveIntegerField(default=0)
  is_active = models.BooleanField(default=True)

  class Meta:
    db_table = 'numberdar_profiles'
    indexes = [models.Index(fields=['jurisdiction_district', 'is_active'])]

  def __str__(self):
    return f"{self.user.full_name}"


class FarmerVerificationRequest(BaseModel):
  STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('escalated', 'Escalated'),
  )
  farmer = models.ForeignKey('accounts.FarmerProfile', on_delete=models.PROTECT, related_name = 'verification_requests')
  numberdar = models.ForeignKey(NumberdarProfile, on_delete=models.PROTECT, related_name = 'verification_requests')
  status = models.CharField(max_length=30, choices=STATUS_CHOICES, default = 'pending', db_index=True)
  submitted_at = models.DateTimeField(auto_now_add=True)
  resolved_at = models.DateTimeField(null=True, blank=True)
  numberdar_notes = models.TextField(blank=True)
  escalated_to = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name = 'escalated_verifications')

  class Meta:
    db_table = 'farmer_verification_requests'
    indexes = [models.Index(fields=['numberdar', 'status']), models.Index(fields=['farmer', 'status'])]

  def __str__(self):
    return f"{self.farmer.user.full_name} - {self.numberdar.user.full_name} ({self.status})"