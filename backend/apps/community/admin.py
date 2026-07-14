from django.contrib import admin
from apps.community.models import NumberdarProfile, FarmerVerificationRequest

@admin.register(NumberdarProfile)
class NumberdarProfileAdmin(admin.ModelAdmin):
  list_display = ['id', 'user', 'jurisdiction_district', 'total_farmers_verified', 'cnic_verified', 'is_active']
  list_editable = ['cnic_verified', 'is_active']
  search_fields = ['user__full_name', 'user__phone', 'jurisdiction_district']
  list_filter = ['jurisdiction_district', 'is_active', 'cnic_verified']

@admin.register(FarmerVerificationRequest)
class FarmerVerificationRequestAdmin(admin.ModelAdmin):
  list_display = ['id', 'farmer', 'numberdar', 'status', 'submitted_at', 'resolved_at']
  list_filter = ['status']
  search_fields = ['farmer__user__full_name', 'numberdar__user__full_name']
  readonly_fields = ['farmer', 'numberdar', 'submitted_at']