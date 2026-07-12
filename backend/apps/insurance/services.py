from decimal import Decimal
from apps.accounts.models import InsuranceProfile
from apps.escrow.models import EscrowTransaction
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from apps.insurance.models import InsurancePolicy, InsuranceClaim

PREMIUM_RATE = Decimal('0.025')

class InsurancePremiumService:

  @staticmethod
  def enroll_and_deduct(loan, escrow):
    with transaction.atomic():
      if InsurancePolicy.objects.filter(loan=loan).exists():
        raise ValueError(f"Loan {loan.id} already has an insurance policy. Cannot enroll twice.")
      premium = (loan.approved_amount * PREMIUM_RATE).quantize(Decimal('0.01'))
      escrow_locked = type(escrow).objects.select_for_update().get(id=escrow.id)
      escrow_locked.insurance_premium_deducted = premium
      escrow_locked.remaining_balance -= premium
      escrow_locked.save(update_fields=['insurance_premium_deducted', 'remaining_balance'])
      insurer = InsuranceProfile.objects.filter(is_primary=True).first()
      EscrowTransaction.objects.create(escrow=escrow, txn_type='insurance', amount=premium, recipient=insurer.user if insurer else loan.bank.user)
      policy = InsurancePolicy.objects.create(loan=loan, insurer=insurer, coverage_amount=loan.approved_amount, premium_amount=premium, status='active',
        policy_start=timezone.now().date(), policy_end=timezone.now().date() + timedelta(days=180))
      return policy

class InsuranceClaimService:
  @staticmethod
  def file_claim(policy_id, claimed_by_user, reason, claim_amount):
    policy = InsurancePolicy.objects.select_related('loan__farmer__user').get(id=policy_id)
    if policy.status == 'expired':
      raise ValueError('cant file a claim on an expired policy.')
    if policy.loan.farmer.user != claimed_by_user:
      raise PermissionError('you can only file a claim on your own policy.')
    claim = InsuranceClaim.objects.create(policy=policy, claimed_by=claimed_by_user, reason=reason, claim_amount=Decimal(str(claim_amount)), status='pending')
    if policy.status == 'active':
      policy.status = 'claimed'
      policy.save(update_fields=['status'])
    return claim

  @staticmethod
  def review_claim(claim_id, reviewer_user, decision, approved_amount=None, reviewer_note=''):
    if decision not in ('approved', 'rejected'):
      raise ValueError("decision must be 'approved' or 'rejected'.")
    with transaction.atomic():
      claim = InsuranceClaim.objects.select_for_update().select_related('policy').get(id=claim_id)
      if claim.status != 'pending':
        raise ValueError(f'the claim is already {claim.status}. cant review again.')
      claim.status = decision
      claim.reviewer_note = reviewer_note
      claim.resolved_at = timezone.now()

      if decision == 'approved':
        if approved_amount is None:
          raise ValueError('the approved_amount is need. when approv a claim.')
        claim.approved_amount = Decimal(str(approved_amount))
        claim.policy.status = 'claimed'
        claim.policy.save(update_fields=['status'])
      else:
        has_other_active_claims = claim.policy.claims.filter(status__in=['pending', 'approved']).exclude(id=claim.id).exists()
        if not has_other_active_claims:
          claim.policy.status = 'active'
          claim.policy.save(update_fields=['status'])
      claim.save()

    return claim