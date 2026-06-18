from rest_framework import serializers

class LoanApprovalSerializer(serializers.Serializer):
  approved_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
  interest_rate_pct = serializers.DecimalField(max_digits=8, decimal_places=2)

  def validate_approved_amount(self, value):
    if value <= 0:
      raise serializers.ValidationError('the approv. amount must be > than zero.')
    return value

  def validate_interest_rate_pct(self, value):
    if value <= 0 or value > 50:
      raise serializers.ValidationError('the interest rate must be b/w 0 and 50 perc.')
    return value

class LoanRejectionSerializer(serializers.Serializer):
  rejection_reason = serializers.CharField(max_length=500)

  def validate_rejection_reason(self, value):
    if not value.strip():
      raise serializers.ValidationError('the rejection reason cant be blank.')
    return value.strip()