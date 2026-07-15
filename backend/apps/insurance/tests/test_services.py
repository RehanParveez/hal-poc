import pytest
from decimal import Decimal, ROUND_DOWN
from apps.insurance.tests.factories import LoanApplicationFactory, EscrowWalletFactory, InsurancePolicyFactory, InsuranceClaimFactory, InsuranceProfileFactory
from apps.insurance.services import InsurancePremiumService, InsuranceClaimService
from apps.escrow.models import EscrowTransaction
from apps.insurance.models import InsurancePolicy, InsuranceClaim
from apps.accounts.tests.factories import UserFactory
from queue import Queue
import threading
from datetime import timedelta
from django.utils import timezone
from django.db import IntegrityError, connections
from apps.accounts.tests.factories import UserFactory
from apps.wallets.models import Wallet

@pytest.mark.django_db
class TestEnrollAndDeductBasics:
  def test_deducts_premium_at_two_point_five_percent(self):
    loan = LoanApplicationFactory(approved_amount=Decimal('100000.00'))
    escrow = EscrowWalletFactory(loan=loan, total_funded=Decimal('100000.00'), remaining_balance=Decimal('100000.00'))
    policy = InsurancePremiumService.enroll_and_deduct(loan, escrow)
    assert policy.premium_amount == Decimal('2500.00')
    escrow.refresh_from_db()
    assert escrow.remaining_balance == Decimal('97500.00')
    assert escrow.insurance_premium_deducted == Decimal('2500.00')

  def test_rounding_defaults_to_half_even_unlike_escrow_s_explicit_round_down(self):
    loan = LoanApplicationFactory(approved_amount=Decimal('40.60'))
    escrow = EscrowWalletFactory(loan=loan, total_funded=Decimal('40.60'), remaining_balance=Decimal('40.60'))
    policy = InsurancePremiumService.enroll_and_deduct(loan, escrow)
    round_down_equivalent = (Decimal('40.60') * Decimal('0.025')).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
    assert round_down_equivalent == Decimal('1.01')
    assert policy.premium_amount == Decimal('1.02')

  def test_policy_coverage_equals_full_approved_amount(self):
    loan = LoanApplicationFactory(approved_amount=Decimal('80000.00'))
    escrow = EscrowWalletFactory(loan=loan, total_funded=Decimal('80000.00'), remaining_balance=Decimal('80000.00'))
    policy = InsurancePremiumService.enroll_and_deduct(loan, escrow)
    assert policy.coverage_amount == Decimal('80000.00')

  def test_policy_covers_exactly_180_days(self):
    loan = LoanApplicationFactory(approved_amount=Decimal('50000.00'))
    escrow = EscrowWalletFactory(loan=loan, total_funded=Decimal('50000.00'), remaining_balance=Decimal('50000.00'))
    policy = InsurancePremiumService.enroll_and_deduct(loan, escrow)
    assert (policy.policy_end - policy.policy_start).days == 180

@pytest.mark.django_db
class TestEnrollAndDeductInsurerAssignment:
  def test_assigns_whichever_insurer_row_is_first_with_no_matching_logic(self): 
    loan = LoanApplicationFactory(approved_amount=Decimal('50000.00'))
    escrow = EscrowWalletFactory(loan=loan, total_funded=Decimal('50000.00'), remaining_balance=Decimal('50000.00'))
    insurer_a = InsuranceProfileFactory(company_name = 'EFU Life')
    insurer_a.is_primary = True
    insurer_a.save()
    Wallet.objects.create(user=insurer_a.user, balance=Decimal('0.00'))
    policy = InsurancePremiumService.enroll_and_deduct(loan, escrow)
    assert policy.insurer_id == insurer_a.id

  def test_falls_back_to_bank_as_recipient_but_policy_gets_no_insurer(self):
    loan = LoanApplicationFactory(approved_amount=Decimal('50000.00'))
    escrow = EscrowWalletFactory(loan=loan, total_funded=Decimal('50000.00'), remaining_balance=Decimal('50000.00'))
    policy = InsurancePremiumService.enroll_and_deduct(loan, escrow)
    assert policy.insurer is None
    assert policy.status == 'active'
    txn = EscrowTransaction.objects.get(escrow=escrow, txn_type = 'insurance')
    assert txn.recipient == loan.bank.user

@pytest.mark.django_db(transaction=True)
class TestEnrollAndDeductAtomicity:
  def test_calling_it_twice_safely_rejects_without_draining_escrow(self):
    loan = LoanApplicationFactory(approved_amount=Decimal('100000.00'))
    escrow = EscrowWalletFactory(loan=loan, total_funded=Decimal('100000.00'), remaining_balance=Decimal('100000.00'))
    InsurancePremiumService.enroll_and_deduct(loan, escrow)
    escrow.refresh_from_db()
    balance_after_first_call = escrow.remaining_balance
    assert balance_after_first_call == Decimal('97500.00')
    with pytest.raises(ValueError):
      InsurancePremiumService.enroll_and_deduct(loan, escrow)
    escrow.refresh_from_db()
    assert escrow.remaining_balance == balance_after_first_call, ("Escrow should not be drained when enrollment fails")
    assert InsurancePolicy.objects.filter(loan=loan).count() == 1
    assert EscrowTransaction.objects.filter(escrow=escrow, txn_type='insurance').count() == 1

@pytest.mark.django_db
class TestFileClaim:
  def test_creates_a_pending_claim_and_flips_active_policy_to_claimed(self):
    policy = InsurancePolicyFactory(status = 'active')
    claim = InsuranceClaimService.file_claim(policy_id=policy.id, claimed_by_user=policy.loan.farmer.user,
      reason = 'Flooding destroyed the wheat crop before harvest', claim_amount=Decimal('25000.00'))
    assert claim.status == 'pending'
    policy.refresh_from_db()
    assert policy.status == 'claimed'

  def test_rejects_a_claim_from_someone_who_is_not_the_policy_s_farmer(self):
    policy = InsurancePolicyFactory(status = 'active')
    other_farmer = UserFactory(role = 'smallholder')
    with pytest.raises(PermissionError):
      InsuranceClaimService.file_claim(policy_id=policy.id, claimed_by_user=other_farmer,
        reason='Attempting to claim on someone elses policy', claim_amount=Decimal('10000.00'))

  def test_rejects_filing_on_an_expired_policy(self):
    policy = InsurancePolicyFactory(status = 'expired')
    with pytest.raises(ValueError):
      InsuranceClaimService.file_claim(policy_id=policy.id, claimed_by_user=policy.loan.farmer.user,
        reason = 'Trying to claim on an expired policy anyway', claim_amount=Decimal('10000.00'))

  def test_filing_is_allowed_when_policy_end_date_has_passed_but_status_was_never_flipped(self):
    policy = InsurancePolicyFactory(status = 'active', policy_end=timezone.now().date() - timedelta(days=30))
    claim = InsuranceClaimService.file_claim(policy_id=policy.id, claimed_by_user=policy.loan.farmer.user,
      reason='Filing on a policy whose end date already passed', claim_amount=Decimal('5000.00'))
    assert claim.status == 'pending'

  def test_a_second_claim_can_be_filed_while_the_first_is_still_pending(self):
    policy = InsurancePolicyFactory(status = 'active', coverage_amount=Decimal('50000.00'))
    farmer_user = policy.loan.farmer.user
    InsuranceClaimService.file_claim(policy_id=policy.id, claimed_by_user=farmer_user,
      reason='First claim -- pest damage to standing crop', claim_amount=Decimal('40000.00'))
    policy.refresh_from_db()
    assert policy.status == 'claimed'
    second_claim = InsuranceClaimService.file_claim(policy_id=policy.id, claimed_by_user=farmer_user,
      reason='Second claim filed on the same still-pending policy', claim_amount=Decimal('40000.00'))
    assert second_claim.status == 'pending'
    assert InsuranceClaim.objects.filter(policy=policy).count() == 2

  def test_claim_amount_can_exceed_the_policy_s_coverage_amount(self):
    policy = InsurancePolicyFactory(status = 'active', coverage_amount=Decimal('50000.00'))
    claim = InsuranceClaimService.file_claim(policy_id=policy.id, claimed_by_user=policy.loan.farmer.user,
      reason='Requesting far more than the policy actually covers', claim_amount=Decimal('999999.00'))
    assert claim.claim_amount == Decimal('999999.00')

@pytest.mark.django_db
class TestReviewClaim:
  def test_approving_sets_approved_amount_and_flips_policy_to_claimed(self):
    claim = InsuranceClaimFactory(status = 'pending', claim_amount=Decimal('20000.00'))
    reviewer = UserFactory(role = 'insurance')
    updated = InsuranceClaimService.review_claim(claim_id=claim.id, reviewer_user=reviewer, decision = 'approved', approved_amount=Decimal('18000.00'))
    assert updated.status == 'approved'
    assert updated.approved_amount == Decimal('18000.00')
    assert updated.resolved_at is not None
    updated.policy.refresh_from_db()
    assert updated.policy.status == 'claimed'

  def test_approving_without_an_approved_amount_is_rejected(self):
    claim = InsuranceClaimFactory(status = 'pending')
    reviewer = UserFactory(role = 'insurance')
    with pytest.raises(ValueError):
      InsuranceClaimService.review_claim(claim_id=claim.id, reviewer_user=reviewer, decision = 'approved', approved_amount=None)

  def test_approved_amount_can_exceed_both_claim_amount_and_policy_coverage(self):
    policy = InsurancePolicyFactory(coverage_amount=Decimal('50000.00'))
    claim = InsuranceClaimFactory(policy=policy, status = 'pending', claim_amount=Decimal('20000.00'))
    reviewer = UserFactory(role = 'insurance')
    updated = InsuranceClaimService.review_claim(claim_id=claim.id, reviewer_user=reviewer, decision = 'approved', approved_amount=Decimal('500000.00'))
    assert updated.approved_amount == Decimal('500000.00')

  def test_rejecting_the_only_pending_claim_reactivates_the_policy(self):
    policy = InsurancePolicyFactory(status = 'claimed')
    claim = InsuranceClaimFactory(policy=policy, status = 'pending')
    reviewer = UserFactory(role = 'insurance')
    InsuranceClaimService.review_claim(claim_id=claim.id, reviewer_user=reviewer, decision = 'rejected', reviewer_note = 'Insufficient evidence')
    policy.refresh_from_db()
    assert policy.status == 'active'

  def test_rejecting_one_claim_does_not_reactivate_while_another_is_still_pending(self):
    policy = InsurancePolicyFactory(status = 'claimed')
    claim_a = InsuranceClaimFactory(policy=policy, status = 'pending')
    InsuranceClaimFactory(policy=policy, status = 'pending')
    reviewer = UserFactory(role = 'insurance')
    InsuranceClaimService.review_claim(claim_id=claim_a.id, reviewer_user=reviewer, decision = 'rejected')
    policy.refresh_from_db()
    assert policy.status == 'claimed'

  def test_rejecting_a_later_claim_reactivates_the_policy_even_after_an_earlier_one_was_approved(self):
    policy = InsurancePolicyFactory(status='active', coverage_amount=Decimal('50000.00'))
    farmer_user = policy.loan.farmer.user
    approved_claim = InsuranceClaimFactory(policy=policy, claimed_by=farmer_user, status = 'pending')
    reviewer = UserFactory(role='insurance')
    InsuranceClaimService.review_claim(claim_id=approved_claim.id, reviewer_user=reviewer, decision = 'approved', approved_amount=Decimal('45000.00'))
    policy.refresh_from_db()
    assert policy.status == 'claimed'
    second_claim = InsuranceClaimService.file_claim(policy_id=policy.id, claimed_by_user=farmer_user,
      reason='A second, unrelated claim filed after the first was approved', claim_amount=Decimal('5000.00'))
    InsuranceClaimService.review_claim(claim_id=second_claim.id, reviewer_user=reviewer, decision = 'rejected')
    policy.refresh_from_db()
    assert policy.status == 'claimed' 

  def test_rejects_reviewing_a_claim_that_is_already_resolved(self):
    claim = InsuranceClaimFactory(status = 'approved')
    reviewer = UserFactory(role = 'insurance')
    with pytest.raises(ValueError):
      InsuranceClaimService.review_claim(claim_id=claim.id, reviewer_user=reviewer, decision = 'rejected')

  def test_rejects_an_invalid_decision_value(self):
    claim = InsuranceClaimFactory(status = 'pending')
    reviewer = UserFactory(role = 'insurance')
    with pytest.raises(ValueError):
      InsuranceClaimService.review_claim(claim_id=claim.id, reviewer_user=reviewer, decision = 'maybe')

@pytest.mark.django_db(transaction=True)
class TestReviewClaimConcurrency:
  def test_concurrent_reviews_of_the_same_claim_only_one_succeeds(self):
    claim = InsuranceClaimFactory(status = 'pending')
    reviewer = UserFactory(role = 'insurance')
    results = Queue()
    barrier = threading.Barrier(2)

    def worker():
      barrier.wait()
      try:
        InsuranceClaimService.review_claim(claim_id=claim.id, reviewer_user=reviewer, decision = 'approved', approved_amount=Decimal('1000.00'))
        results.put('success')
      except ValueError:
        results.put('failure')
      finally:
        connections.close_all()
    threads = [threading.Thread(target=worker) for _ in range(2)]
    for t in threads: t.start()
    for t in threads: t.join()

    outcomes = list(results.queue)
    assert outcomes.count('success') == 1
    assert outcomes.count('failure') == 1