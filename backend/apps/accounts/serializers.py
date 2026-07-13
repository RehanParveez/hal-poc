from rest_framework import serializers
from apps.accounts.models import User
from shared.validators import validate_secp_number, validate_ntn

class UserRegistrationSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True, style={'input_type': 'password'})
  SELF_REGISTERABLE_ROLES = ('smallholder', 'tenant', 'landowner', 'shopkeeper')
  role = serializers.ChoiceField(choices=[(r, r) for r in SELF_REGISTERABLE_ROLES])
  shop_name = serializers.CharField(max_length=180, required=False, allow_blank=True)
  secp_registration_number = serializers.CharField(required=False, allow_blank=True, validators=[validate_secp_number])
  ntn_number = serializers.CharField(required=False, allow_blank=True, validators=[validate_ntn])

  class Meta:
    model = User
    fields = ['id', 'phone', 'cnic', 'full_name', 'password', 'role', 'district', 'province', 'shop_name', 'secp_registration_number', 'ntn_number']
    read_only_fields = ['id']
  
  def validate(self, data):
    if data.get('role') == 'shopkeeper':
      if not data.get('shop_name', '').strip():
        raise serializers.ValidationError({'shop_name': 'Shop name is need. for shopkeeper registration.'})
      if not data.get('secp_registration_number', '').strip():
        raise serializers.ValidationError({'secp_registration_number': 'SECP registration number is need.'})
      if not data.get('ntn_number', '').strip():
        raise serializers.ValidationError({'ntn_number': 'NTN number is need.'})
    return data

  def create(self, validated_data):
    password = validated_data.pop('password')
    shop_name = validated_data.pop('shop_name', '')
    secp_number = validated_data.pop('secp_registration_number', '')
    ntn_number = validated_data.pop('ntn_number', '')
    user = User.objects.create_user(password=password, **validated_data)
    if user.role == 'shopkeeper':
      if secp_number:
        user.secp_registration_number = secp_number
        user.save(update_fields=['secp_registration_number'])
      if shop_name or ntn_number:
        profile = user.shopkeeper_profile
        if shop_name:
          profile.shop_name = shop_name
        if ntn_number:
          profile.ntn_number = ntn_number
        profile.save(update_fields=['shop_name', 'ntn_number'])
    return user

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id', 'phone', 'cnic', 'full_name', 'role', 'district', 'province', 'is_verified', 'numberdar_verified', 'credit_tier', 'secp_verified', 'ntn_verified']
    read_only_fields = ['id', 'role', 'is_verified', 'numberdar_verified', 'credit_tier', 'secp_verified', 'ntn_verified']