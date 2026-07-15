from django.contrib import admin
from apps.credit.models import CreditCheck, OTPConsent

@admin.register(CreditCheck)
class CreditCheckAdmin(admin.ModelAdmin):
  list_display = ['id', 'farmer', 'status', 'risk_tier', 'credit_score', 'is_eligible', 'requested_at', 'completed_at']
  list_filter = ['status', 'risk_tier', 'is_eligible']
  search_fields = ['farmer__user__full_name', 'cnic_number', 'bank_reference_id']
  readonly_fields = [f.name for f in CreditCheck._meta.fields]

@admin.register(OTPConsent)
class OTPConsentAdmin(admin.ModelAdmin):
  list_display = ['id', 'user', 'verified', 'expires_at', 'created_at']
  list_filter = ['verified']
  readonly_fields = ['user', 'purpose', 'phone_sent_to', 'otp_hash', 'expires_at']