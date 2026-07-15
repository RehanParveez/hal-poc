from decimal import Decimal, ROUND_DOWN
from apps.crops.models import CropLifecycleMilestone
from apps.escrow.models import EscrowWallet, EscrowMilestoneUnlock
from django.db import transaction
from django.utils import timezone
from apps.notifications.services import NotificationService
from apps.insurance.services import InsurancePremiumService

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
    
    InsurancePremiumService.enroll_and_deduct(loan, escrow)  
    escrow.refresh_from_db()
    
    unlock_amount = (approved * phase_1.unlock_pct / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
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
      transaction.on_commit(lambda: NotificationService.notify(escrow.loan.farmer.user, 'escrow_phase_unlocked',
       {'phase_number': next_milestone.phase_number, 'phase_name': next_milestone.phase_name,
        'allowed_categories': ', '.join(next_milestone.allowed_input_categories)}, reference_id=escrow.id))
    return next_milestone
