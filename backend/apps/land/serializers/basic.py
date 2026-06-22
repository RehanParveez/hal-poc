from rest_framework import serializers
from apps.land.models import Land, TenantAgreement
from apps.accounts.models import User, FarmerProfile

class LandSerializer(serializers.ModelSerializer):
  available_acres = serializers.ReadOnlyField()
  landowner_name = serializers.CharField(source = 'landowner.user.full_name', read_only=True)

  class Meta:
    model = Land
    fields = ['id', 'parcel_ref', 'district', 'tehsil', 'total_acres', 'available_acres',
      'arazi_verified', 'landowner_name', 'created_at']
    read_only_fields = ['id', 'arazi_verified', 'created_at', 'landowner_name']

  def validate_total_acres(self, value):
    if value <= 0:
      raise serializers.ValidationError('the Acres must be > than zero.')
    return value

  def validate_parcel_ref(self, value):
    if not value.strip():
      raise serializers.ValidationError('the Parcel refer cant be blank.')
    return value.strip()

class TenantAgreementSerializer(serializers.ModelSerializer):
  tenant_phone = serializers.CharField(write_only=True)
  class Meta:
    model = TenantAgreement
    fields = [
      'id', 'tenant_phone', 'parcel', 'agreement_type', 'leased_acres', 'season', 'theka_amount', 'farmer_share_pct', 'landowner_share_pct',
      'status', 'landowner_approved', 'approved_at', 'rejected_reason', 'created_at']
    read_only_fields = ['id', 'status', 'landowner_approved', 'approved_at', 'rejected_reason', 'created_at']
    
  def create(self, validated_data):
    phone = validated_data.pop('tenant_phone')
    try:
      user_instance = User.objects.get(phone=phone)
      profile = FarmerProfile.objects.get(user=user_instance)
    except (User.DoesNotExist, FarmerProfile.DoesNotExist):
      raise serializers.ValidationError({"tenant_phone": "no farmer pres. with this phone number."})
    validated_data['tenant'] = profile
    return super().create(validated_data)

  def validate(self, data):
    agreement_type = data.get('agreement_type')
    parcel = data.get('parcel')
    leased_acres = data.get('leased_acres')

    if agreement_type == 'batai':
      fs = data.get('farmer_share_pct')
      ls = data.get('landowner_share_pct')
      if fs is None or ls is None:
        raise serializers.ValidationError('the Batai agrees require both farmer_share_pct & landowner_share_pct.')
      if abs((float(fs) + float(ls)) - 100) > 0.01:
        raise serializers.ValidationError(f'the Batai shares must add up to 100%. You entered {fs} + {ls} = {float(fs) + float(ls)}.')

    if agreement_type == 'theka':
      if not data.get('theka_amount'):
        raise serializers.ValidationError('Theka agrees require a theka_amount a fixed rent in PKR.')

    if parcel and leased_acres:
      if leased_acres > parcel.available_acres:
        raise serializers.ValidationError(f'You req {leased_acres} acres but this parcel only has {parcel.available_acres} acres avail.')
      if leased_acres <= 0:
        raise serializers.ValidationError('the leased acres must be > than zero.')

    return data