from rest_framework import serializers
from apps.loans.models import LoanApplication

class LoanApplicationSerializer(serializers.ModelSerializer):
  class Meta:
    model = LoanApplication
    fields = ['id', 'farmer', 'bank', 'tenant_agreement', 'crop', 'acres_applied_for', 'requested_amount', 'approved_amount',
      'interest_rate_pct', 'status', 'rejection_reason', 'loan_recovered_to_date', 'approved_at', 'disbursed_at',
      'created_at', 'updated_at']
    read_only_fields = ['id', 'status', 'approved_amount', 'interest_rate_pct', 'rejection_reason', 'loan_recovered_to_date',
      'approved_at', 'disbursed_at', 'created_at', 'updated_at']

  def validate(self, data):
    farmer = data.get('farmer')
    tenant_agreement = data.get('tenant_agreement')
    acres_applied_for = data.get('acres_applied_for')
    requested_amount = data.get('requested_amount')

    if acres_applied_for <= 0:
      raise serializers.ValidationError('the acres applied for must be > than zero.')

    if requested_amount <= 0:
      raise serializers.ValidationError('the requested amount must be > than zero.')

    if farmer and farmer.user.role == 'tenant':
      if not tenant_agreement:
        raise serializers.ValidationError('the tenant farmers must provide an appro. tenant agreem.')
      if not tenant_agreement.landowner_approved:
        raise serializers.ValidationError('the tenant agreem. must be appro. by the landowner before applying for a loan.')
      if tenant_agreement.tenant != farmer:
        raise serializers.ValidationError('this tenant agreem does not belong to you.')
      if acres_applied_for > tenant_agreement.leased_acres:
        raise serializers.ValidationError(f'You applied for {acres_applied_for} acres but your tenant agreem '
          f'only covers {tenant_agreement.leased_acres} acres.')

    if farmer and farmer.user.role == 'smallholder':
      if tenant_agreement:
        raise serializers.ValidationError('the Smallholder farmers do not need a tenant agreem.')
      if acres_applied_for > farmer.total_owned_acres:
        raise serializers.ValidationError(f'you applied for {acres_applied_for} acres but you only own '
          f'{farmer.total_owned_acres} acres.')

    return data

class LoanApplicationSerializer1(serializers.ModelSerializer):
  farmer_name = serializers.CharField(source = 'farmer.user.full_name', read_only=True)
  farmer_phone = serializers.CharField(source = 'farmer.user.phone', read_only=True)
  farmer_district = serializers.CharField(source = 'farmer.user.district', read_only=True)
  farmer_province = serializers.CharField(source = 'farmer.user.province', read_only=True)
  farmer_owned_acres = serializers.DecimalField(source='farmer.total_owned_acres', max_digits=12, decimal_places=2, read_only=True)
  bank_name = serializers.CharField(source = 'bank.institution_name', read_only=True)
  crop_name = serializers.CharField(source = 'crop.name', read_only=True)
  crop_code = serializers.CharField(source = 'crop.code', read_only=True)
  crop_season = serializers.CharField(source = 'crop.season', read_only=True)
  tenant_agreement_type = serializers.CharField(source = 'tenant_agreement.agreement_type', read_only=True)
  tenant_agreement_acres = serializers.DecimalField(source = 'tenant_agreement.leased_acres', max_digits=12, decimal_places=2, read_only=True)
  tenant_parcel_ref = serializers.CharField(source = 'tenant_agreement.parcel.parcel_ref', read_only=True)
  landowner_name = serializers.CharField(source = 'tenant_agreement.parcel.landowner.user.full_name', read_only=True)
  landowner_approved = serializers.BooleanField(source = 'tenant_agreement.landowner_approved', read_only=True)
  escrow_id = serializers.SerializerMethodField()
  farmer_credit_tier = serializers.CharField(source = 'farmer.user.credit_tier', read_only=True)
  
  def get_escrow_id(self, obj):
    try:
      return str(obj.escrow.id)
    except Exception:
      return None
    
  class Meta:
    model = LoanApplication
    fields = ['id', 'farmer', 'bank', 'tenant_agreement', 'crop', 'acres_applied_for', 'requested_amount', 'approved_amount',
      'interest_rate_pct', 'status', 'rejection_reason', 'loan_recovered_to_date', 'approved_at', 'disbursed_at',
      'created_at', 'updated_at', 'farmer_name', 'farmer_phone', 'farmer_district', 'farmer_province', 'farmer_owned_acres',
      'bank_name', 'crop_name', 'crop_code', 'crop_season', 'tenant_agreement_type', 'tenant_agreement_acres',
      'tenant_parcel_ref', 'landowner_name', 'landowner_approved', 'escrow_id', 'farmer_credit_tier', 'numberdar_verified_at_application']
    read_only_fields = ['id', 'status', 'approved_amount', 'interest_rate_pct', 'rejection_reason', 'loan_recovered_to_date',
      'approved_at', 'disbursed_at', 'created_at', 'updated_at', 'farmer_name', 'farmer_phone', 'farmer_district',
      'farmer_province', 'farmer_owned_acres', 'bank_name', 'crop_name', 'crop_code', 'crop_season',
      'tenant_agreement_type', 'tenant_agreement_acres', 'tenant_parcel_ref', 'landowner_name', 'landowner_approved', 'escrow_id', 'farmer_credit_tier', 'numberdar_verified_at_application']