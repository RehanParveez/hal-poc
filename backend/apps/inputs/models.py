from django.db import models
from shared.models import BaseModel
 
class InputSupplyRequest(BaseModel):
  INPUT_CATEGORIES = (
    ('seed', 'Seed'),
    ('fertilizer', 'Fertilizer'),
    ('pesticide', 'Pesticide'),
    ('irrigation', 'Irrigation'),
    ('labour', 'Labour'),
  )
  STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('paid', 'Paid'),
  )
  escrow = models.ForeignKey('escrow.EscrowWallet', on_delete=models.PROTECT, related_name = 'supply_requests')
  shopkeeper = models.ForeignKey('accounts.ShopkeeperProfile', on_delete=models.PROTECT, related_name = 'received_requests')
  input_category = models.CharField(max_length=50, choices=INPUT_CATEGORIES)
  item_description = models.CharField(max_length=300, blank=True)
  requested_amount = models.DecimalField(max_digits=14, decimal_places=2)
  afo_cap_at_time = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
  status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending', db_index=True)
 
  class Meta:
    db_table = 'input_supply_requests'
    indexes = [models.Index(fields=['escrow', 'input_category']), models.Index(fields=['shopkeeper', 'status']), models.Index(fields=['status'])]
 
  def __str__(self):
    return f"{self.input_category}"