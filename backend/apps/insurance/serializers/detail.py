from rest_framework import serializers
from apps.insurance.models import InsurancePolicy, InsuranceClaim
from django.utils import timezone
from apps.insurance.serializers.basic import InsuranceClaimBasicSerializer

class LoanSummarySerializer(serializers.Serializer):
  id = serializers.UUIDField()
  farmer_name = serializers.SerializerMethodField()
  farmer_district = serializers.SerializerMethodField()
  crop_name = serializers.SerializerMethodField()
  crop_season = serializers.SerializerMethodField()
  acres_applied_for = serializers.DecimalField(max_digits=14, decimal_places=2)
  approved_amount = serializers.DecimalField(max_digits=16, decimal_places=2)
  status = serializers.CharField()

  def get_farmer_name(self, obj):
    return obj.farmer.user.full_name

  def get_farmer_district(self, obj):
    return obj.farmer.user.district

  def get_crop_name(self, obj):
    return obj.crop.name

  def get_crop_season(self, obj):
    return obj.crop.season

class InsurerSummarySerializer(serializers.Serializer):
  id = serializers.UUIDField(source = 'user.id')
  company_name = serializers.CharField()
  full_name = serializers.CharField(source = 'user.full_name')
  phone = serializers.CharField(source = 'user.phone')

class InsurancePolicyDetailSerializer(serializers.ModelSerializer):
  loan = serializers.SerializerMethodField()
  insurer = serializers.SerializerMethodField()
  insurer_name = serializers.SerializerMethodField()
  days_left = serializers.SerializerMethodField()
  claims = InsuranceClaimBasicSerializer(many=True, read_only=True)
  claims_count = serializers.SerializerMethodField()
  has_pending_claim = serializers.SerializerMethodField()

  class Meta:
    model = InsurancePolicy
    fields = ['id', 'loan', 'insurer', 'insurer_name', 'coverage_amount', 'premium_amount', 'status', 'policy_start', 'policy_end',
      'days_left', 'claims', 'claims_count', 'has_pending_claim', 'created_at', 'updated_at']

  def get_loan(self, obj):
    return LoanSummarySerializer(obj.loan).data

  def get_insurer(self, obj):
    return InsurerSummarySerializer(obj.insurer).data if obj.insurer else None

  def get_insurer_name(self, obj):
    return obj.insurer.company_name if obj.insurer else None

  def get_days_left(self, obj):
    today = timezone.now().date()
    return max(0, (obj.policy_end - today).days) if obj.policy_end >= today else 0

  def get_claims_count(self, obj):
    return obj.claims.count()

  def get_has_pending_claim(self, obj):
    return obj.claims.filter(status='pending').exists()

class InsuranceClaimDetailSerializer(serializers.ModelSerializer):
  policy_id = serializers.UUIDField(source = 'policy.id', read_only=True)
  policy_status = serializers.CharField(source = 'policy.status', read_only=True)
  coverage_amount = serializers.DecimalField(source = 'policy.coverage_amount', max_digits=14, decimal_places=2, read_only=True)
  farmer_name = serializers.CharField(source ='claimed_by.full_name', read_only=True)
  farmer_phone = serializers.CharField(source = 'claimed_by.phone', read_only=True)
  farmer_district = serializers.CharField(source = 'claimed_by.district', read_only=True)
  crop_name = serializers.SerializerMethodField()
  loan_amount = serializers.SerializerMethodField()

  class Meta:
    model = InsuranceClaim
    fields = ['id', 'policy_id', 'policy_status', 'coverage_amount', 'farmer_name', 'farmer_phone', 'farmer_district', 'crop_name', 'loan_amount', 'reason',
      'claim_amount', 'approved_amount', 'status', 'reviewer_note', 'resolved_at', 'created_at', 'updated_at']

  def get_crop_name(self, obj):
    return obj.policy.loan.crop.name

  def get_loan_amount(self, obj):
    return obj.policy.loan.approved_amount