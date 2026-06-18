from django.contrib import admin
from apps.insurance.models import InsurancePolicy, InsuranceClaim

@admin.register(InsurancePolicy)
class InsurancePolicyAdmin(admin.ModelAdmin):
  list_display = ('id', 'loan', 'insurer', 'status', 'coverage_amount', 'premium_amount', 'policy_start', 'policy_end')
  list_filter = ('status', 'policy_start', 'policy_end')
  search_fields = ('loan__farmer__user__full_name', 'status')
  raw_id_fields = ('loan', 'insurer')
  list_select_related = ('loan', 'insurer')

@admin.register(InsuranceClaim)
class InsuranceClaimAdmin(admin.ModelAdmin):
  list_display = ('id','policy', 'claimed_by', 'status', 'claim_amount', 'approved_amount', 'resolved_at')
  list_filter = ('status', 'resolved_at')
  search_fields = ('policy__loan__farmer__user__full_name', 'claimed_by__full_name', 'status')
  raw_id_fields = ('policy', 'claimed_by')
  list_select_related = ('policy', 'claimed_by')