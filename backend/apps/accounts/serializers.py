from rest_framework import serializers
from apps.accounts.models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True, style={'input_type': 'password'})
  SELF_REGISTERABLE_ROLES = ('smallholder', 'tenant', 'landowner', 'shopkeeper')
  role = serializers.ChoiceField(choices=[(r, r) for r in SELF_REGISTERABLE_ROLES])

  class Meta:
    model = User
    fields = ['id', 'phone', 'cnic', 'full_name', 'password', 'role', 'district', 'province']
    read_only_fields = ['id']

  def create(self, validated_data):
    password = validated_data.pop('password')
    user = User.objects.create_user(password=password, **validated_data)
    return user

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id', 'phone', 'cnic', 'full_name', 'role', 'district', 'province', 'is_verified']
    read_only_fields = ['id', 'role', 'is_verified']