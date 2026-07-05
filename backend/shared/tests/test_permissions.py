import pytest
from shared.permissions import FarmerPermission, TenantFarmerPerm, LandownerPerm, BankManagerPerm, FactoryPerm, ShopkeeperPerm, InsuranceAgentPerm, AFOOfficerPerm, AdminPerm
from unittest.mock import Mock

ALL_ROLES = ['smallholder', 'tenant', 'landowner', 'bank', 'factory', 'shopkeeper', 'insurance', 'afo', 'admin', None, 'unknown_role']

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

def make_request(role, authenticated=True):
  request = Mock()
  request.user.is_authenticated = authenticated
  request.user.role = role
  return request

@pytest.mark.parametrize("perm_class,allowed_roles", PERMISSION_ROLE_MAP.items())
def test_permission_matrix_grants_only_intended_roles(perm_class, allowed_roles):
  perm = perm_class()
  for role in ALL_ROLES:
    request = make_request(role=role, authenticated=True)
    result = perm.has_permission(request, view=None)
    if role in allowed_roles:
      assert result is True, f"{perm_class.__name__} should ALLOW role='{role}' but denied it"
    else:
      assert result is False, f"{perm_class.__name__} should DENY role='{role}' but allowed it"

@pytest.mark.parametrize("perm_class", PERMISSION_ROLE_MAP.keys())
def test_permission_denies_unauthenticated_user_even_with_correct_role(perm_class):
  perm = perm_class()
  for role in PERMISSION_ROLE_MAP[perm_class]:
    request = make_request(role=role, authenticated=False)
    assert perm.has_permission(request, view=None) is False