from shared.models import BaseModel
from django.db import models

class SettlementInvoice(BaseModel):
  STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('advanced', 'Advanced'),
    ('factsettl', 'FactSettl'),
    ('complete', 'Complete'),
  )
  batch = models.OneToOneField('delivery.BatchDelivery', on_delete=models.PROTECT, related_name = 'invoice')
  loan = models.ForeignKey('loans.LoanApplication', on_delete=models.PROTECT, related_name = 'invoices')
  tenant_agreement = models.ForeignKey('land.TenantAgreement', on_delete=models.PROTECT, related_name = 'invoices', null=True, blank=True)
  gross_payout = models.DecimalField(max_digits=14, decimal_places=2)
  proportional_principal_deduction = models.DecimalField(max_digits=14, decimal_places=2)
  bank_interest_deduction = models.DecimalField(max_digits=14, decimal_places=2)
  bank_factoring_commission = models.DecimalField(max_digits=14, decimal_places=2)
  platform_transaction_fee = models.DecimalField(max_digits=14, decimal_places=2)
  theka_payment = models.DecimalField(max_digits=14, decimal_places=2, default=0)
  batai_landowner_share = models.DecimalField(max_digits=14, decimal_places=2, default=0)
  farmer_net_profit = models.DecimalField(max_digits=14, decimal_places=2)
  insurance_claim_triggered = models.BooleanField(default=False)
  status = models.CharField(max_length=25, choices=STATUS_CHOICES, default = 'pending', db_index=True)
  bank_advanced_at = models.DateTimeField(null=True, blank=True)
  factory_paid_at = models.DateTimeField(null=True, blank=True)

  class Meta:
    db_table = 'settlement_invoices'
    indexes = [models.Index(fields=['loan', 'status']), models.Index(fields=['status'])]

  def __str__(self):
    return f"invoice({self.loan.farmer.user.full_name}"