from rest_framework import serializers
from apps.community.models import NumberdarProfile, FarmerVerificationRequest

class NumberdarProfileSerializer(serializers.ModelSerializer):
  full_name = serializers.CharField(source = 'user.full_name', read_only=True)
  phone = serializers.CharField(source = 'user.phone', read_only=True)

  class Meta:
    model = NumberdarProfile
    fields = ['id', 'full_name', 'phone', 'jurisdiction_district', 'jurisdiction_villages', 'total_farmers_verified', 'is_active']
    read_only_fields = fields

class FarmerVerificationRequestSerializer(serializers.ModelSerializer):
  farmer_name = serializers.CharField(source = 'farmer.user.full_name', read_only=True)
  farmer_phone = serializers.CharField(source = 'farmer.user.phone', read_only=True)
  farmer_district = serializers.CharField(source = 'farmer.user.district', read_only=True)
  numberdar_name = serializers.CharField(source = 'numberdar.user.full_name', read_only=True)

  class Meta:
    model = FarmerVerificationRequest
    fields = ['id', 'farmer', 'farmer_name', 'farmer_phone', 'farmer_district', 'numberdar', 'numberdar_name',
      'status', 'submitted_at', 'resolved_at', 'numberdar_notes', 'created_at']
    read_only_fields = ['id', 'farmer_name', 'farmer_phone', 'farmer_district', 'numberdar_name', 'status', 'submitted_at', 'resolved_at', 'created_at']


class VerificationRejectSerializer(serializers.Serializer):
  notes = serializers.CharField(max_length=550, required=False, allow_blank=True, default='')