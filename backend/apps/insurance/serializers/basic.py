from rest_framework import serializers
from apps.insurance.models import InsurancePolicy, InsuranceClaim
from django.utils import timezone

class InsurancePolicyBasicSerializer(serializers.ModelSerializer):
  farmer_name = serializers.CharField(source='loan.farmer.user.full_name', read_only=True)
  loan_id = serializers.UUIDField(source='loan.id', read_only=True)
  insurer_name = serializers.SerializerMethodField()
  days_left = serializers.SerializerMethodField()

  class Meta:
    model = InsurancePolicy
    fields = ['id', 'loan_id', 'farmer_name', 'insurer_name', 'coverage_amount', 'premium_amount', 'status', 'policy_start', 'policy_end', 'days_left', 'created_at']

  def get_insurer_name(self, obj):
    return obj.insurer.company_name if obj.insurer else None

  def get_days_left(self, obj):
    today = timezone.now().date()
    return max(0, (obj.policy_end - today).days) if obj.policy_end >= today else 0

class InsuranceClaimBasicSerializer(serializers.ModelSerializer):
  farmer_name = serializers.CharField(source='claimed_by.full_name', read_only=True)
  policy_id = serializers.UUIDField(source='policy.id', read_only=True)
  class Meta:
    model = InsuranceClaim
    fields = ['id', 'policy_id', 'farmer_name', 'claim_amount', 'approved_amount', 'status', 'created_at']

class InsuranceClaimCreateSerializer(serializers.Serializer):
  reason = serializers.CharField(min_length=14, max_length=1000)
  claim_amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=1.00)

  def validate_claim_amount(self, value):
    if value <= 0:
      raise serializers.ValidationError("the claim amount must be > than zero.")
    return value

class InsuranceClaimReviewSerializer(serializers.Serializer):
  DECISIONS = [('approved', 'Approved'), ('rejected', 'Rejected')]
  decision = serializers.ChoiceField(choices=DECISIONS)
  approved_amount = serializers.DecimalField(max_digits=16, decimal_places=2, required=False, allow_null=True)
  reviewer_note = serializers.CharField(max_length=500, required=False, allow_blank=True, default='')

  def validate(self, data):
    if data.get('decision') == 'approved' and not data.get('approved_amount'):
      raise serializers.ValidationError({'approved_amount': 'approved_amount is need. when approv. a claim.'})
    return data