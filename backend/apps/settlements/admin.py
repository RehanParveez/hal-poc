from django.contrib import admin
from apps.settlements.models import SettlementInvoice

@admin.register(SettlementInvoice)
class SettlementInvoiceAdmin(admin.ModelAdmin):
  list_display = ['id', 'get_farmer_name', 'status', 'gross_payout', 'farmer_net_profit', 'insurance_claim_triggered']
  list_filter = ['status', 'insurance_claim_triggered']
  search_fields = ['loan__farmer__user__full_name', 'batch__id', 'loan__id']
  autocomplete_fields = ['batch', 'loan', 'tenant_agreement']

  def get_farmer_name(self, obj):
    return obj.loan.farmer.user.full_name
  get_farmer_name.short_description = 'Farmer Name'