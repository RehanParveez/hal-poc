from decimal import Decimal, ROUND_DOWN
from apps.crops.models import CropLifecycleMilestone, CropInputCap
from apps.escrow.models import EscrowWallet, EscrowTransaction, EscrowMilestoneUnlock
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum
from shared.exceptions import AFOLimitExceededError, WrongPhaseForCategoryError, NoActivePhaseError, NotEnoughEscrowError
from apps.wallets.services import WalletService

INSURANCE_PREMIUM_RATE = Decimal('0.025')

class EscrowCreationService:
  @staticmethod
  def create(loan):
   with transaction.atomic():
    loan.refresh_from_db()
    if loan.approved_amount is None:
      raise ValueError(f"Cannot create escrow: Loan {loan.id} has no 'approved_amount'. Check your 'approve_loan' service logic.")
    try:
      phase_1 = CropLifecycleMilestone.objects.get(crop=loan.crop, phase_number=1)
    except CropLifecycleMilestone.DoesNotExist:
      raise ValueError(f"no phase 1 milest configur for crop '{loan.crop.code}'.")
    approved = loan.approved_amount
    escrow = EscrowWallet.objects.create(loan=loan, total_funded=approved, remaining_balance=approved)
    premium = (approved * INSURANCE_PREMIUM_RATE).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
    escrow.insurance_premium_deducted = premium
    escrow.remaining_balance -= premium
    escrow.save(update_fields=['insurance_premium_deducted', 'remaining_balance'])

    insurance_txn = EscrowTransaction.objects.create(escrow=escrow, txn_type = 'insurance', amount=premium, recipient=loan.bank.user, input_category='')
    WalletService.credit_wallet(loan.bank.user.wallet, amount=premium, txn_type = 'insurance', reference_id=insurance_txn.id, note='Insurance premium')
    unlock_amount = (escrow.total_funded * phase_1.unlock_pct / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
    EscrowMilestoneUnlock.objects.create(escrow=escrow, milestone=phase_1, unlocked_amount=unlock_amount, unlocked_at=timezone.now(),
      is_active=True)
    return escrow

  @staticmethod
  def unlock_next_phase(escrow_id):
    with transaction.atomic():
      escrow = EscrowWallet.objects.select_for_update().get(id=escrow_id)
      current = escrow.unlocks.filter(is_active=True).select_related('milestone').first()
      if not current:
        raise ValueError('there is no active phase pres on this escrow.')
      next_milestone = CropLifecycleMilestone.objects.filter(crop=escrow.loan.crop, phase_number=current.milestone.phase_number + 1
      ).first()
      if not next_milestone:
        raise ValueError('the all phases are compl.')

      unlock_amount = (escrow.remaining_balance * next_milestone.unlock_pct / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
      current.is_active = False
      current.save(update_fields=['is_active'])
      EscrowMilestoneUnlock.objects.create(escrow=escrow, milestone=next_milestone, unlocked_amount=unlock_amount, unlocked_at=timezone.now(),
        is_active=True)
    return next_milestone

class InputPaymentService:
  @staticmethod
  def process_payment(escrow_id, shopkeeper_user, input_category, requested_amount, item_description=''):
    amount = Decimal(str(requested_amount))
    with transaction.atomic():
      escrow = EscrowWallet.objects.select_for_update().get(id=escrow_id)
      active_unlock = escrow.unlocks.filter(is_active=True).select_related('milestone').first()

      if not active_unlock:
        raise NoActivePhaseError()
      allowed = active_unlock.milestone.allowed_input_categories
      if input_category not in allowed:
        raise WrongPhaseForCategoryError(requested_category=input_category, current_phase_name=active_unlock.milestone.phase_name, allowed_categories=allowed)
      cumulative_unlocked = escrow.unlocks.aggregate(total=Sum('unlocked_amount'))['total'] or Decimal('0')
      phase_available = cumulative_unlocked - escrow.total_spent_on_inputs
      if amount > phase_available:
        raise NotEnoughEscrowError(requested=amount, available=max(phase_available, Decimal('0')))
      try:
        cap_record = CropInputCap.objects.get(crop=escrow.loan.crop, district=escrow.loan.farmer.user.district, input_category=input_category,
          valid_season=escrow.loan.crop.season)
      except CropInputCap.DoesNotExist:
        raise AFOLimitExceededError(category=input_category, requested=amount, cap_total=Decimal('0'), already_spent=Decimal('0'))

      acres_for_loan = escrow.loan.acres_applied_for
      cap_total = (cap_record.max_cost_per_acre * acres_for_loan).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

      already_spent = EscrowTransaction.objects.filter(escrow=escrow, txn_type='input', input_category=input_category,
      ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
      remaining_cap = cap_total - already_spent

      if amount > remaining_cap:
        raise AFOLimitExceededError(category=input_category, requested=amount, cap_total=cap_total, already_spent=already_spent)
      if amount > escrow.remaining_balance:
        raise ValueError(f"Insufficient escrow balance. Trying to spend {amount} but only {escrow.remaining_balance} remains.")
      escrow.total_spent_on_inputs += amount
      escrow.remaining_balance -= amount
      escrow.save(update_fields=['total_spent_on_inputs', 'remaining_balance'])

      txn = EscrowTransaction.objects.create(escrow=escrow, txn_type='input', amount=amount, recipient=shopkeeper_user,
        input_category=input_category, afo_cap_snapshot=cap_record.max_cost_per_acre)
      WalletService.credit_wallet(shopkeeper_user.wallet, amount=amount, txn_type='input', reference_id=txn.id, note=f"Escrow input payment: {input_category}")

    return txn