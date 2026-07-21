from rest_framework import serializers
from apps.credit.models import CreditCheck

class RequestOTPSerializer(serializers.Serializer):
  loan_id = serializers.UUIDField(required=False, allow_null=True)

class VerifyOTPSerializer(serializers.Serializer):
  otp_reference = serializers.UUIDField()
  otp_code = serializers.CharField(min_length=6, max_length=6)

class TriggerCreditCheckSerializer(serializers.Serializer):
  otp_reference = serializers.UUIDField()
  loan_id = serializers.UUIDField()

class CreditCheckSerializer1(serializers.ModelSerializer):
  farmer_name = serializers.CharField(source = 'farmer.user.full_name', read_only=True)

  class Meta:
    model = CreditCheck
    fields = ['id', 'farmer', 'farmer_name', 'loan_application', 'status', 'risk_tier', 'credit_score', 'total_outstanding_debt', 'default_history_flag', 
      'active_micro_loans_count', 'ecib_status', 'max_approved_limit_pkr', 'is_eligible', 'bank_reference_id',
      'bank_decision_notes', 'requested_at', 'completed_at']
    read_only_fields = fields

class CreditCheckSerializer(serializers.ModelSerializer):
  farmer_name = serializers.CharField(source = 'farmer.user.full_name', read_only=True)

  class Meta:
    model = CreditCheck
    fields = ['id', 'farmer', 'farmer_name', 'loan_application', 'status', 'risk_tier', 'credit_score', 'total_outstanding_debt', 'default_history_flag', 
      'active_micro_loans_count', 'ecib_status', 'max_approved_limit_pkr', 'is_eligible', 'bank_reference_id', 'bank_decision_notes',
      'raw_bank_response', 'requested_at', 'completed_at']
    read_only_fields = fields