from django.db import models
from shared.models import BaseModel

class BatchDelivery(BaseModel):
  STATUS_CHOICES = (('in_transit', 'In Transit'), ('received', 'Received'), ('grade_confirmed', 'Grade Confirmed'), ('payment_triggered', 'Payment Triggered'))
  allocation = models.ForeignKey('contracts.FarmerContractAllocation', on_delete=models.PROTECT, related_name = 'batches')
  batch_kg = models.DecimalField(max_digits=12, decimal_places=2)
  expected_payout = models.DecimalField(max_digits=14, decimal_places=2)
  actual_payout = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
  grade_received = models.CharField(max_length=25, blank=True)
  grade_deduction_pct = models.DecimalField(max_digits=7, decimal_places=2, default=0)
  grade_notes = models.TextField(blank=True)
  status = models.CharField(max_length=35, choices=STATUS_CHOICES, default='in_transit', db_index=True)
  delivered_at = models.DateTimeField(null=True, blank=True)
  grade_confirmed_at = models.DateTimeField(null=True, blank=True)

  class Meta:
    db_table = 'batch_deliveries'
    indexes = [models.Index(fields=['allocation', 'status']), models.Index(fields=['status'])]

  def __str__(self):
    return f"{self.batch_kg}"