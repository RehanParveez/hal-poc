from rest_framework import serializers
from apps.accounts.models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True, style={'input_type': 'password'})
  SELF_REGISTERABLE_ROLES = ('smallholder', 'tenant', 'landowner', 'shopkeeper')
  role = serializers.ChoiceField(choices=[(r, r) for r in SELF_REGISTERABLE_ROLES])
  shop_name = serializers.CharField(max_length=180, required=False, allow_blank=True)

  class Meta:
    model = User
    fields = ['id', 'phone', 'cnic', 'full_name', 'password', 'role', 'district', 'province', 'shop_name']
    read_only_fields = ['id']
  
  def validate(self, data):
    if data.get('role') == 'shopkeeper' and not data.get('shop_name', '').strip():
      raise serializers.ValidationError({'shop_name': 'Shop name is needed for the shopkeeper registration.'})
    return data

  def create(self, validated_data):
    password = validated_data.pop('password')
    shop_name = validated_data.pop('shop_name', '')
    user = User.objects.create_user(password=password, **validated_data)
    if user.role == 'shopkeeper' and shop_name:
      user.shopkeeper_profile.shop_name = shop_name
      user.shopkeeper_profile.save(update_fields=['shop_name'])
    return user

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id', 'phone', 'cnic', 'full_name', 'role', 'district', 'province', 'is_verified']
    read_only_fields = ['id', 'role', 'is_verified']