import pytest
from shared.permissions import FarmerPermission, TenantFarmerPerm, LandownerPerm, BankManagerPerm, FactoryPerm, ShopkeeperPerm, InsuranceAgentPerm, AFOOfficerPerm, AdminPerm
from apps.accounts.models import User
from apps.accounts.tests.factories import UserFactory
from rest_framework.test import APIClient

PERMISSION_ROLE_MAP = {
  FarmerPermission: {'smallholder', 'tenant'},
  TenantFarmerPerm: {'tenant'},
  LandownerPerm: {'landowner'},
  BankManagerPerm: {'bank'},
  FactoryPerm: {'factory'},
  ShopkeeperPerm: {'shopkeeper'},
  InsuranceAgentPerm: {'insurance'},
  AFOOfficerPerm: {'afo'},
  AdminPerm: {'admin'},
}

def test_user_roles_choices_match_permission_map_exactly():
  model_roles = {value for value, _ in User.ROLES}
  covered_roles = set().union(*PERMISSION_ROLE_MAP.values())
  assert model_roles == covered_roles, (
    f"In User.ROLES but no permission class covers it: {model_roles - covered_roles}. "
    f"Covered by a permission class but not a real role: {covered_roles - model_roles}.")

@pytest.mark.django_db
@pytest.mark.parametrize("perm_class,allowed_roles", PERMISSION_ROLE_MAP.items())
def test_permission_matrix_against_real_user_rows(rf, perm_class, allowed_roles):
  for role_value, _ in User.ROLES:
    user = UserFactory(role=role_value)
    request = rf.get('/')
    request.user = user
    result = perm_class().has_permission(request, view=None)
    expected = role_value in allowed_roles
    assert result is expected, (
      f"{perm_class.__name__} with real User(role='{role_value}') "
      f"returned {result}, expected {expected}")
    
LOGIN_URL = '/accounts/tokenobtainpair/'
REFRESH_URL = '/accounts/tokenrefresh/'
PROTECTED_URL = '/wallets/balances/my_balance/'

@pytest.mark.django_db
class TestJWTLogin:
  def test_valid_credentials_return_access_and_refresh_tokens(self):
    UserFactory(role = 'smallholder', phone = '03001234567', password = 'correct-pass')
    client = APIClient()
    response = client.post(LOGIN_URL, {'phone': '03001234567', 'password': 'correct-pass'})
    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data

  def test_wrong_password_is_rejected(self):
    UserFactory(role = 'smallholder', phone = '03001234567', password = 'correct-pass')
    client = APIClient()
    response = client.post(LOGIN_URL, {'phone': '03001234567', 'password': 'wrong-pass'})
    assert response.status_code == 401

  def test_nonexistent_phone_is_rejected(self):
    client = APIClient()
    response = client.post(LOGIN_URL, {'phone': '03009999999', 'password': 'whatever'})
    assert response.status_code == 401

  def test_access_token_from_login_actually_authenticates_a_protected_endpoint(self):
    user = UserFactory(role = 'smallholder', phone = '03001234567', password = 'correct-pass')
    client = APIClient()
    login_response = client.post(LOGIN_URL, {'phone': '03001234567', 'password': 'correct-pass'})
    access_token = login_response.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    response = client.get(PROTECTED_URL)
    assert response.status_code == 200
    assert response.data['id'] == str(user.wallet.id)

  def test_garbage_token_is_rejected(self):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Bearer not-a-real-token')
    response = client.get(PROTECTED_URL)
    assert response.status_code == 401

  def test_refresh_token_produces_a_new_access_token(self):
    UserFactory(role = 'smallholder', phone = '03001234567', password = 'correct-pass')
    client = APIClient()
    login_response = client.post(LOGIN_URL, {'phone': '03001234567', 'password': 'correct-pass'})
    response = client.post(REFRESH_URL, {'refresh': login_response.data['refresh']})
    assert response.status_code == 200
    assert 'access' in response.data