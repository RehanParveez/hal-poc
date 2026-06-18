from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

class AFOLimitExceededError(Exception):
  def __init__(self, category, requested, cap_total, already_spent):
    self.category = category
    self.requested = requested
    self.cap = cap_total
    self.already_spent = already_spent
    self.remaining_allowed = cap_total - already_spent 
    super().__init__(f"Cannot spend {requested} on {category}. "
      f"Cap is {cap_total}, already spent {already_spent}.")

class NotEnoughEscrowError(Exception):
  def __init__(self, requested, available):
    self.requested = requested
    self.available = available

class WrongPhaseForCategoryError(Exception):
  def __init__(self, requested_category, current_phase_name, allowed_categories):
    self.category = requested_category
    self.current_phase = current_phase_name
    self.allowed = allowed_categories
    super().__init__(f"Category '{requested_category}' not allowed in phase '{current_phase_name}'")

class AcreageCeilingExceededError(Exception):
  def __init__(self, requested, available):
    self.requested = requested
    self.available = available

class LoanAlreadyDisbursedError(Exception):
  pass

class NoActivePhaseError(Exception):
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