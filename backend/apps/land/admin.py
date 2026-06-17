from django.contrib import admin
from apps.land.models import Land, TenantAgreement

@admin.register(Land)
class LandAdmin(admin.ModelAdmin):
  list_display = ('parcel_ref', 'landowner', 'district', 'total_acres', 'arazi_verified')
  list_filter = ('district', 'arazi_verified')
  search_fields = ('parcel_ref', 'landowner__user__full_name')

@admin.register(TenantAgreement)
class TenantAgreementAdmin(admin.ModelAdmin):
  list_display = ('tenant', 'parcel', 'agreement_type', 'season', 'status')
  list_filter = ('status', 'agreement_type', 'season')
  search_fields = ('tenant__user__full_name', 'parcel__parcel_ref')