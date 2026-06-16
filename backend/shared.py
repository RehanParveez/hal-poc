from rest_framework.permissions import BasePermission
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

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

class AFOLimitExceededError(Exception):
  def __init__(self, category, requested, cap, already_spent):
    self.category = category
    self.requested = requested
    self.cap = cap
    self.already_spent = already_spent

class NotEnoughEscrowError(Exception):
  def __init__(self, requested, available):
    self.requested = requested
    self.available = available

class WrongPhaseForCategoryError(Exception):
  def __init__(self, category, current_phase, allowed):
    self.category = category
    self.current_phase = current_phase
    self.allowed = allowed

class AcreageCeilingExceededError(Exception):
  def __init__(self, requested, available):
    self.requested = requested
    self.available = available

class LoanAlreadyDisbursedError(Exception):
  pass

class ContractFullyAllocatedError(Exception):
  def __init__(self, requested, available):
    self.requested = requested
    self.available = available

def custom_exception_handler(exc, context):
  response = exception_handler(exc, context)

  if isinstance(exc, AFOLimitExceededError):
    return Response({'error': 'AFO_LIMIT_EXCEEDED', 'category': exc.category, 'requested_amount': str(exc.requested),
      'afo_cap_total': str(exc.cap), 'already_spent': str(exc.already_spent), 'remaining_allowed': str(max(exc.cap - exc.already_spent, 0)),
      'message': (
        f"Payment blocked. AFO limit for '{exc.category}' "
        f"on your registered acreage is PKR {exc.cap}. "
        f"Already spent: PKR {exc.already_spent}."
      )}, status=status.HTTP_400_BAD_REQUEST)

  if isinstance(exc, NotEnoughEscrowError):
    return Response({'error': 'INSUFFICIENT_ESCROW',  'requested': str(exc.requested), 'available': str(exc.available),
      'message': f"Escrow balance PKR {exc.available} is less than requested PKR {exc.requested}." }, status=status.HTTP_400_BAD_REQUEST)

  if isinstance(exc, WrongPhaseForCategoryError):
    return Response({'error': 'INVALID_PHASE_FOR_CATEGORY', 'category': exc.category, 'current_phase': exc.current_phase,
      'allowed_categories': exc.allowed, 'message': (f"'{exc.category}' cannot be purchased in phase '{exc.current_phase}'. "
        f"Allowed: {', '.join(exc.allowed)}.")}, status=status.HTTP_400_BAD_REQUEST)

  if isinstance(exc, AcreageCeilingExceededError):
    return Response({'error': 'ACREAGE_CEILING_EXCEEDED', 'requested_acres': str(exc.requested), 'available_acres': str(exc.available),
      'message': f"Requested {exc.requested} acres exceeds registered ceiling of {exc.available} acres."
    }, status=status.HTTP_400_BAD_REQUEST)

  if isinstance(exc, LoanAlreadyDisbursedError):
    return Response({'error': 'LOAN_ALREADY_DISBURSED', 'message': "This loan has already been disbursed. Double-spend prevented."
    }, status=status.HTTP_409_CONFLICT)

  if isinstance(exc, ContractFullyAllocatedError):
    return Response({'error': 'CONTRACT_FULLY_ALLOCATED', 'requested_kg': str(exc.requested), 'available_kg': str(exc.available),
      'message': f"Contract has only {exc.available} kg remaining." }, status=status.HTTP_409_CONFLICT)
  return response