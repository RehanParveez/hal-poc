import pytest
from shared.permissions import FarmerPermission, TenantFarmerPerm, LandownerPerm, BankManagerPerm, FactoryPerm, ShopkeeperPerm, InsuranceAgentPerm, AFOOfficerPerm, AdminPerm
from apps.accounts.models import User
from apps.accounts.tests.factories import UserFactory

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