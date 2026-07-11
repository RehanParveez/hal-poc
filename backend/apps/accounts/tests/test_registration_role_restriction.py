import pytest
from rest_framework.test import APIClient

REGISTER_URL = '/accounts/users/'

@pytest.mark.django_db
class TestRegistrationRoleRestriction:
  @pytest.mark.parametrize("role", ['smallholder', 'tenant', 'landowner', 'shopkeeper'])
  def test_public_roles_can_self_register(self, role):
    response = APIClient().post(REGISTER_URL, {
      'phone': f'0300{role[:6]}1', 'cnic': f'35202-{role[:7]}-1', 'full_name': 'Test User', 'password': 'testpass123', 'role': role, 'district': 'Faisalabad'})
    assert response.status_code == 201

  @pytest.mark.parametrize("role", ['admin', 'bank', 'factory', 'insurance', 'afo'])
  def test_institutional_roles_are_now_rejected_from_public_signup(self, role):
    response = APIClient().post(REGISTER_URL, {'phone': f'0311{role[:6]}1', 'cnic': f'35202-{role[:7]}-2', 'full_name': 'Test User',
      'password': 'pass12312', 'role': role, 'district': 'Faisalabad'})
    assert response.status_code == 400