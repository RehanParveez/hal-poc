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
    super().__init__(f"not enough escrow: requested {requested}, available {available}")

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
    super().__init__(f"Acreage ceiling exceeded: requested {requested}, available {available}")

class LoanAlreadyDisbursedError(Exception):
  def __init__(self):
    super().__init__("this loan has already been disbursed.")

class NoActivePhaseError(Exception):
  def __init__(self):
    super().__init__("there is no active phase for this operation.")

class CorporateNotVerifiedError(Exception):
  def __init__(self, role_label = 'this account'):
    self.role_label = role_label
    super().__init__(f"{role_label} has not completed SECP/NTN verification yet.")

class ContractFullyAllocatedError(Exception):
  def __init__(self, requested, available):
    self.requested = requested
    self.available = available
    super().__init__(f"contract fully allocated: requested {requested}, available {available}")
    
class OutOfJurisdictionError(Exception):
  def __init__(self, farmer_district, numberdar_district):
    self.farmer_district = farmer_district
    self.numberdar_district = numberdar_district
    super().__init__(f"Numberdar covers '{numberdar_district}' but farmer is in '{farmer_district}'.")

class DuplicateVerificationRequestError(Exception):
  def __init__(self):
    super().__init__("you already have a pending or approved verification request.")

class NumberdarVerificationRequiredError(Exception):
  def __init__(self):
    super().__init__("this farmer has not been verified by a Numberdar yet. Loans can't be disbursed.")
    
class ConsentNotVerifiedError(Exception):
  def __init__(self):
    super().__init__("otp consent must be verified before running a credit check.")

class CreditCheckRequiredError(Exception):
  def __init__(self):
    super().__init__("credit check must be completed and approved before this loan can be disbursed.")

class CreditBureauRejectedError(Exception):
  def __init__(self, message = 'credit bureau rejected the request.'):
    self.message = message
    super().__init__(message)

class ExternalServiceUnavailable(Exception):
  def __init__(self, service_name='external service'):
    self.service_name = service_name
    super().__init__(f"{service_name} is currently unavailable. Please try again shortly.")

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
    
  if isinstance(exc, NoActivePhaseError):
    return Response({'error': 'NO_ACTIVE_PHASE', 'message': "there is no active phase for this operation."
    }, status=status.HTTP_400_BAD_REQUEST)
    
  if isinstance(exc, CorporateNotVerifiedError): 
    return Response({'error': 'CORPORATE_NOT_VERIFIED',
      'message': "This shopkeeper's business registration is still pending verification. "
        "transaction cannot proceed until an admin confirms SECP/NTN details."
    }, status=status.HTTP_403_FORBIDDEN)
  
  if isinstance(exc, OutOfJurisdictionError):
    return Response({'error': 'OUT_OF_JURISDICTION', 'farmer_district': exc.farmer_district,
      'numberdar_district': exc.numberdar_district, 'message': str(exc)}, status=status.HTTP_403_FORBIDDEN)

  if isinstance(exc, DuplicateVerificationRequestError):
    return Response({'error': 'DUPLICATE_VERIFICATION_REQUEST', 'message': str(exc)}, status=status.HTTP_409_CONFLICT)

  if isinstance(exc, NumberdarVerificationRequiredError):
    return Response({'error': 'NUMBERDAR_VERIFICATION_REQUIRED', 'message': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
  
  if isinstance(exc, ConsentNotVerifiedError):
    return Response({'error': 'CONSENT_NOT_VERIFIED', 'message': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

  if isinstance(exc, CreditCheckRequiredError):
    return Response({'error': 'CREDIT_CHECK_REQUIRED', 'message': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

  if isinstance(exc, CreditBureauRejectedError):
    return Response({'error': 'CREDIT_BUREAU_REJECTED', 'message': exc.message}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

  if isinstance(exc, ExternalServiceUnavailable):
    return Response({'error': 'EXTERNAL_SERVICE_UNAVAILABLE', 'message': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
  
  return response
