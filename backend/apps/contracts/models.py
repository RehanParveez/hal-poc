from shared.models import BaseModel
from django.db import models

class CropContract(BaseModel):
  STATUS_CHOICES = (
    ('open', 'Open'),
    ('allocated', 'Allocated'),
    ('completed', 'Completed'),
  )
  factory = models.ForeignKey('accounts.FactoryProfile', on_delete=models.PROTECT, related_name = 'contracts')
  crop = models.ForeignKey('crops.CropType', on_delete=models.PROTECT, related_name = 'contracts')
  required_kg = models.DecimalField(max_digits=16, decimal_places=2)
  allocated_kg = models.DecimalField(max_digits=16, decimal_places=2, default=0)
  base_price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
  payment_defer_days = models.PositiveSmallIntegerField(default=20)
  quality_grade_expected = models.CharField(max_length=25, default = 'Grade A')
  status = models.CharField(max_length=30, choices=STATUS_CHOICES, default = 'open', db_index=True)
  delivery_deadline = models.DateField()

  class Meta:
    db_table = 'crop_contracts'
    indexes = [models.Index(fields=['crop', 'status']), models.Index(fields=['factory', 'status'])]

  def __str__(self):
    return f"{self.factory.factory_name}"

  @property
  def remaining_kg(self):
    return self.required_kg - self.allocated_kg

class FarmerContractAllocation(BaseModel):
  contract = models.ForeignKey(CropContract, on_delete=models.PROTECT, related_name = 'allocations')
  farmer = models.ForeignKey('accounts.FarmerProfile', on_delete=models.PROTECT, related_name = 'contract_allocations')
  loan = models.ForeignKey('loans.LoanApplication', on_delete=models.PROTECT, related_name = 'contract_allocations')
  committed_kg = models.DecimalField(max_digits=10, decimal_places=2)

  class Meta:
    db_table = 'farmer_contract_allocations'
    unique_together = [['contract', 'farmer']]
    indexes = [models.Index(fields=['contract', 'farmer']), models.Index(fields=['farmer'])]

  def __str__(self):
    return f"{self.farmer.user.full_name}"