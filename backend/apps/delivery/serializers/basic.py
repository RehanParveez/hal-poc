from rest_framework import serializers
from apps.delivery.models import BatchDelivery

class BatchDeliverySerializer(serializers.ModelSerializer):
  class Meta:
    model = BatchDelivery
    fields = ['id', 'allocation', 'batch_kg', 'expected_payout', 'actual_payout', 'grade_received', 'grade_deduction_pct', 'grade_notes', 'status', 'delivered_at', 
      'grade_confirmed_at', 'created_at']
    read_only_fields = ['id', 'expected_payout', 'actual_payout', 'grade_received', 'grade_deduction_pct', 'grade_notes', 'status',
      'delivered_at', 'grade_confirmed_at', 'created_at']

  def validate_batch_kg(self, value):
    if value <= 0:
      raise serializers.ValidationError("the batch kg must be > than zero.")
    return value

class GradeConfirmationSerializer(serializers.Serializer):
  grade_received = serializers.CharField(max_length=20)
  grade_deduction_pct = serializers.DecimalField(max_digits=5, decimal_places=2, default=0)
  grade_notes = serializers.CharField(max_length=500, required=False, allow_blank=True)

  def validate_grade_deduction_pct(self, value):
    if value < 0 or value > 100:
      raise serializers.ValidationError("Grade deduction percentage must be between 0 and 100.")
    return value