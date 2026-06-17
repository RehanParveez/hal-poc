from rest_framework import serializers
from apps.land.models import TenantAgreement

class TenantAgreementDetailSerializer(serializers.ModelSerializer):
  tenant_name = serializers.CharField(source = 'tenant.user.full_name', read_only=True)
  tenant_phone = serializers.CharField(source = 'tenant.user.phone', read_only=True)
  tenant_district = serializers.CharField(source = 'tenant.user.district', read_only=True)
  parcel_ref = serializers.CharField(source = 'parcel.parcel_ref', read_only=True)
  parcel_district = serializers.CharField(source = 'parcel.district', read_only=True)
  parcel_total_acres = serializers.DecimalField(source = 'parcel.total_acres', max_digits=12, decimal_places=2, read_only=True)
  landowner_name = serializers.CharField(source = 'parcel.landowner.user.full_name', read_only=True)

  class Meta:
    model = TenantAgreement
    fields = ['id', 'parcel', 'agreement_type', 'leased_acres', 'season', 'theka_amount', 'farmer_share_pct', 'landowner_share_pct',
      'status', 'landowner_approved', 'approved_at', 'rejected_reason', 'created_at', 'tenant_name', 'tenant_phone', 'tenant_district',
      'parcel_ref', 'parcel_district', 'parcel_total_acres', 'landowner_name']
    read_only_fields = fields