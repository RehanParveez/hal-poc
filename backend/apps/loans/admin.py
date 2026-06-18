from django.contrib import admin
from apps.loans.models import LoanApplication

@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
  list_display = ['id', 'farmer', 'bank', 'crop', 'acres_applied_for', 'requested_amount', 'approved_amount', 'interest_rate_pct',
    'status', 'is_active', 'created_at']
  search_fields = ['farmer__user__full_name', 'farmer__user__phone', 'farmer__user__cnic', 'bank__institution_name']
  list_filter = ['status', 'crop', 'is_active']