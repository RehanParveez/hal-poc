import re
from rest_framework import serializers

def validate_secp_number(value):
  if not re.match(r'^SECP-NTN-\d{8}$', value):
    raise serializers.ValidationError('SECP number must be in the format SECP-NTN-XXXXXXXX (8 digits).')
  return value

def validate_ntn(value):
  if not re.match(r'^\d{7}$', value):
    raise serializers.ValidationError('NTN must be exactly 7 digits.')
  return value