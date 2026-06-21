import logging
from django.db import transaction
from apps.escrow.models import EscrowWallet, EscrowTransaction
from shared.exceptions import NoActivePhaseError, WrongPhaseForCategoryError, AFOLimitExceededError, NotEnoughEscrowError
from apps.crops.models import CropInputCap
from decimal import Decimal
from django.db.models import Sum
from apps.inputs.models import InputSupplyRequest
from apps.wallets.models import Wallet
from apps.wallets.services import WalletService

logger = logging.getLogger(__name__)

def process_input_request(escrow_id, shopkeeper_profile, input_category, amount, description=''):
  with transaction.atomic():
    escrow = EscrowWallet.objects.select_for_update().get(id=escrow_id)
    loan = escrow.loan
    active_unlock = escrow.unlocks.filter(is_active=True).select_related('milestone').first()
    if not active_unlock:
      raise NoActivePhaseError()
    allowed = active_unlock.milestone.allowed_input_categories
    if input_category not in allowed:
      raise WrongPhaseForCategoryError(requested_category=input_category, current_phase_name=active_unlock.milestone.phase_name, allowed_categories=allowed)
  
    try:
      cap_obj = CropInputCap.objects.get(crop=loan.crop, district=escrow.project_district, input_category=input_category, valid_season=loan.crop.season)
    except CropInputCap.DoesNotExist:
      raise AFOLimitExceededError(category=input_category, requested=amount, cap_total=Decimal('0'), already_spent=Decimal('0'))
    max_allowed = cap_obj.max_cost_per_acre * loan.acres_applied_for
    already_spent = escrow.transactions.filter(txn_type='input', input_category=input_category).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    if (already_spent + amount) > max_allowed:
      raise AFOLimitExceededError(category=input_category, requested=amount, cap_total=max_allowed, already_spent=already_spent)
    if amount > escrow.remaining_balance:
      raise NotEnoughEscrowError(requested=amount, available=escrow.remaining_balance)
  
    escrow.total_spent_on_inputs += amount
    escrow.remaining_balance -= amount
    escrow.save(update_fields=['total_spent_on_inputs', 'remaining_balance'])
    EscrowTransaction.objects.create(escrow=escrow, txn_type='input', amount=amount, recipient=shopkeeper_profile.user, input_category=input_category, 
      afo_cap_snapshot=max_allowed)
    supply_request = InputSupplyRequest.objects.create(escrow=escrow, shopkeeper=shopkeeper_profile, input_category=input_category, item_description=description, 
      requested_amount=amount, afo_cap_at_time=max_allowed, status='paid')
    shopkeeper_wallet = Wallet.objects.get(user=shopkeeper_profile.user)
    WalletService.credit_wallet(wallet=shopkeeper_wallet, amount=amount, txn_type='input', reference_id=supply_request.id, 
      note=f"input payment: {input_category} from farmer {loan.farmer.user.full_name}")
    logger.info(f"[AFO GATE PASSED] Escrow {escrow_id} | Category: {input_category} | Amount: PKR {amount} | Cap: {max_allowed} | Already spent: {already_spent}")
    print(f"[SHOPKEEPER PAYMENT APPROVED] PKR {amount} logged for {shopkeeper_profile.user.full_name}. (Wallet integration pending).")
  return supply_request