from rest_framework.permissions import BasePermission

class FarmerPermission(BasePermission):
  def has_permission(self, request, view):
    if not request.user.is_authenticated:
      return False
    if getattr(request.user, 'role', None) in ('smallholder', 'tenant'):
      return True
    return False

class TenantFarmerPerm(BasePermission):
  def has_permission(self, request, view):
    if not request.user.is_authenticated:
      return False
    if getattr(request.user, 'role', None) == 'tenant':
      return True
    return False

class LandownerPerm(BasePermission):
  def has_permission(self, request, view):
    if not request.user.is_authenticated:
      return False
    if getattr(request.user, 'role', None) == 'landowner':
      return True
    return False

class BankManagerPerm(BasePermission):
  def has_permission(self, request, view):
    if not request.user.is_authenticated:
      return False
    if getattr(request.user, 'role', None) == 'bank':
      return True
    return False

class FactoryPerm(BasePermission):
  def has_permission(self, request, view):
    if not request.user.is_authenticated:
      return False
    if getattr(request.user, 'role', None) == 'factory':
      return True
    return False

class ShopkeeperPerm(BasePermission):
  def has_permission(self, request, view):
    if not request.user.is_authenticated:
      return False
    if getattr(request.user, 'role', None) == 'shopkeeper':
      return True
    return False

class InsuranceAgentPerm(BasePermission):
  def has_permission(self, request, view):
    if not request.user.is_authenticated:
      return False
    if getattr(request.user, 'role', None) == 'insurance':
      return True
    return False

class AFOOfficerPerm(BasePermission):
  def has_permission(self, request, view):
    if not request.user.is_authenticated:
      return False
    if getattr(request.user, 'role', None) == 'afo':
      return True
    return False

class AdminPerm(BasePermission):
  def has_permission(self, request, view):
    if not request.user.is_authenticated:
      return False
    if getattr(request.user, 'role', None) == 'admin':
      return True
    return False