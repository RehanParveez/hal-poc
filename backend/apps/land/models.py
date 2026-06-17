from shared.models import BaseModel
from django.db import models
from django.db.models import Sum
import uuid

class Land(BaseModel):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  landowner = models.ForeignKey('accounts.LandownerProfile', on_delete=models.PROTECT, related_name = 'parcels')
  parcel_ref = models.CharField(max_length=100, unique=True)
  district = models.CharField(max_length=110, db_index=True)
  tehsil = models.CharField(max_length=110, blank=True)
  total_acres = models.DecimalField(max_digits=10, decimal_places=2)
  arazi_verified = models.BooleanField(default=True)
  
  class Meta:
    db_table = 'land'
    indexes = [models.Index(fields=['district']), models.Index(fields=['landowner'])]

  def __str__(self):
    return f"{self.parcel_ref}"

  @property
  def available_acres(self):
    used = self.agreements.filter(status = 'active').aggregate(total=Sum('leased_acres'))['total'] or 0
    return self.total_acres - used

class TenantAgreement(BaseModel):
  AGREEMENT_TYPES = (
    ('theka', 'Theka'),
    ('batai', 'Batai'),
  )
  
  STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('active', 'Active'),
    ('completed', 'Completed'),
    ('rejected', 'Rejected'),
  )
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  tenant = models.ForeignKey('accounts.FarmerProfile', on_delete=models.PROTECT, related_name = 'tenant_agreements')
  parcel = models.ForeignKey(Land, on_delete=models.PROTECT, related_name = 'agreements')
  agreement_type = models.CharField(max_length=10, choices=AGREEMENT_TYPES)
  leased_acres = models.DecimalField(max_digits=10, decimal_places=2)
  season = models.CharField(max_length=30)
  theka_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
  farmer_share_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
  landowner_share_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default = 'pending')
  landowner_approved = models.BooleanField(default=False)
  approved_at = models.DateTimeField(null=True, blank=True)
  rejected_reason = models.TextField(blank=True)

  class Meta:
    db_table = 'tenant_agreements'
    unique_together = [['tenant', 'parcel', 'season']]
    indexes = [models.Index(fields=['tenant', 'status']), models.Index(fields=['parcel', 'season'])]

  def __str__(self):
    return f"{self.tenant.user.full_name}"