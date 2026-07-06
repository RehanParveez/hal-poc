import threading
from decimal import Decimal
from queue import Queue
import pytest
from django.db import connections, IntegrityError
from django.db.models import Sum
from django.db.models.deletion import ProtectedError
from apps.accounts.tests.factories import UserFactory
from apps.escrow.models import EscrowWallet, EscrowMilestoneUnlock, EscrowTransaction
from apps.escrow.services import EscrowCreationService, InputPaymentService
from apps.escrow.tests.factories import LoanApplicationFactory, CropLifecycleMilestoneFactory, CropInputCapFactory
from apps.crops.models import CropInputCap
from shared.exceptions import AFOLimitExceededError, WrongPhaseForCategoryError, NoActivePhaseError, NotEnoughEscrowError

def build_escrow(unlock_pct=Decimal('30.00'), allowed=('seed',), cap_per_acre=Decimal('2000.00'),
    acres=Decimal('5.00'), approved=Decimal('100000.00')):
  loan = LoanApplicationFactory(approved_amount=approved, acres_applied_for=acres)
  CropLifecycleMilestoneFactory(crop=loan.crop, phase_number=1, unlock_pct=unlock_pct, allowed_input_categories=list(allowed))
  CropInputCapFactory(crop=loan.crop, district=loan.farmer.user.district, input_category = 'seed',
    valid_season=loan.crop.season, max_cost_per_acre=cap_per_acre)
  return EscrowCreationService.create(loan)

@pytest.mark.django_db
class TestEscrowCreationServiceCreate:
  def test_deducts_insurance_premium_at_correct_rate(self):
    loan = LoanApplicationFactory(approved_amount=Decimal('100000.00'))
    CropLifecycleMilestoneFactory(crop=loan.crop, phase_number=1, unlock_pct=Decimal('30.00'))
    escrow = EscrowCreationService.create(loan)
    assert escrow.insurance_premium_deducted == Decimal('2500.00')
    assert escrow.remaining_balance == Decimal('97500.00')

  def test_unlocks_phase_1_using_total_funded_not_remaining_balance(self):
    loan = LoanApplicationFactory(approved_amount=Decimal('100000.00'))
    CropLifecycleMilestoneFactory(crop=loan.crop, phase_number=1, unlock_pct=Decimal('30.00'))
    escrow = EscrowCreationService.create(loan)
    unlock = escrow.unlocks.get(is_active=True)
    assert unlock.unlocked_amount == Decimal('30000.00')

  def test_logs_insurance_transaction_and_credits_bank_s_real_wallet(self):
    loan = LoanApplicationFactory(approved_amount=Decimal('100000.00'))
    CropLifecycleMilestoneFactory(crop=loan.crop, phase_number=1)
    balance_before = loan.bank.user.wallet.balance
    escrow = EscrowCreationService.create(loan)
    txn = escrow.transactions.get(txn_type = 'insurance')
    assert txn.amount == Decimal('2500.00')
    assert txn.recipient == loan.bank.user
    loan.bank.user.wallet.refresh_from_db()
    assert loan.bank.user.wallet.balance == balance_before + Decimal('2500.00')

  def test_raises_when_loan_has_no_approved_amount(self):
    loan = LoanApplicationFactory(approved_amount=None)
    with pytest.raises(ValueError):
      EscrowCreationService.create(loan)

  def test_raises_when_no_phase_1_milestone_configured(self):
    loan = LoanApplicationFactory(approved_amount=Decimal('50000.00'))
    with pytest.raises(ValueError):
      EscrowCreationService.create(loan)

  def test_create_is_atomic_no_partial_escrow_survives_a_mid_failure(self, monkeypatch):
    loan = LoanApplicationFactory(approved_amount=Decimal('50000.00'))
    CropLifecycleMilestoneFactory(crop=loan.crop, phase_number=1)

    def boom(*args, **kwargs):
      raise RuntimeError("simulated failure")

    monkeypatch.setattr(EscrowMilestoneUnlock.objects, 'create', boom)
    
    with pytest.raises(RuntimeError):
      EscrowCreationService.create(loan)
    assert EscrowWallet.objects.filter(loan=loan).count() == 0, (
      "a wallet+premium+transaction survived even though milestone-unlock creation failed -- "
      "the atomic() wrapper isn't rolling back correctly"
    )

@pytest.mark.django_db
class TestEscrowCreationServiceUnlockNextPhase:
  def test_deactivates_current_and_activates_next(self):
    loan = LoanApplicationFactory(approved_amount=Decimal('100000.00'))
    phase1 = CropLifecycleMilestoneFactory(crop=loan.crop, phase_number=1, unlock_pct=Decimal('30.00'))
    phase2 = CropLifecycleMilestoneFactory(crop=loan.crop, phase_number=2, unlock_pct=Decimal('40.00'))
    escrow = EscrowCreationService.create(loan)
    next_milestone = EscrowCreationService.unlock_next_phase(escrow.id)
    assert next_milestone == phase2
    escrow.refresh_from_db()
    assert escrow.unlocks.get(milestone=phase1).is_active is False
    assert escrow.unlocks.get(milestone=phase2).is_active is True

  def test_unlock_amount_uses_remaining_balance_not_total_funded(self):
    loan = LoanApplicationFactory(approved_amount=Decimal('100000.00'))
    CropLifecycleMilestoneFactory(crop=loan.crop, phase_number=1, unlock_pct=Decimal('30.00'))
    phase2 = CropLifecycleMilestoneFactory(crop=loan.crop, phase_number=2, unlock_pct=Decimal('50.00'))
    escrow = EscrowCreationService.create(loan)
    EscrowCreationService.unlock_next_phase(escrow.id)
    escrow.refresh_from_db()
    assert escrow.unlocks.get(milestone=phase2).unlocked_amount == Decimal('48750.00')

  def test_raises_when_no_active_phase_exists(self):
    loan = LoanApplicationFactory(approved_amount=Decimal('50000.00'))
    CropLifecycleMilestoneFactory(crop=loan.crop, phase_number=1)
    escrow = EscrowCreationService.create(loan)
    escrow.unlocks.update(is_active=False)
    with pytest.raises(ValueError):
      EscrowCreationService.unlock_next_phase(escrow.id)

  def test_raises_when_all_phases_already_completed(self):
    loan = LoanApplicationFactory(approved_amount=Decimal('50000.00'))
    CropLifecycleMilestoneFactory(crop=loan.crop, phase_number=1)
    escrow = EscrowCreationService.create(loan)
    with pytest.raises(ValueError):
      EscrowCreationService.unlock_next_phase(escrow.id)

@pytest.mark.django_db
class TestInputPaymentServiceGuardRails:

  def test_rejects_category_not_allowed_in_current_phase(self):
    escrow = build_escrow(allowed=('seed',))
    shopkeeper = UserFactory(role = 'shopkeeper')
    with pytest.raises(WrongPhaseForCategoryError):
      InputPaymentService.process_payment(escrow.id, shopkeeper, 'fertilizer', Decimal('500.00'))

  def test_rejects_when_no_active_phase(self):
    escrow = build_escrow()
    escrow.unlocks.update(is_active=False)
    shopkeeper = UserFactory(role = 'shopkeeper')
    with pytest.raises(NoActivePhaseError):
      InputPaymentService.process_payment(escrow.id, shopkeeper, 'seed', Decimal('500.00'))

  def test_rejects_when_no_afo_cap_record_exists_for_category(self):
    escrow = build_escrow(allowed=('seed', 'fertilizer'))
    shopkeeper = UserFactory(role = 'shopkeeper')
    with pytest.raises(AFOLimitExceededError):
      InputPaymentService.process_payment(escrow.id, shopkeeper, 'fertilizer', Decimal('500.00'))

  def test_rejects_spending_beyond_the_afo_cap(self):
    escrow = build_escrow(unlock_pct=Decimal('100.00'), cap_per_acre=Decimal('2000.00'), acres=Decimal('5.00'))
    shopkeeper = UserFactory(role = 'shopkeeper')
    with pytest.raises(AFOLimitExceededError) as exc_info:
      InputPaymentService.process_payment(escrow.id, shopkeeper, 'seed', Decimal('10000.01'))
    assert exc_info.value.cap == Decimal('10000.00')

  def test_allows_spending_exactly_up_to_the_afo_cap(self):
    escrow = build_escrow(unlock_pct=Decimal('100.00'), cap_per_acre=Decimal('2000.00'), acres=Decimal('5.00'))
    shopkeeper = UserFactory(role = 'shopkeeper')
    txn = InputPaymentService.process_payment(escrow.id, shopkeeper, 'seed', Decimal('10000.00'))
    assert txn.amount == Decimal('10000.00')

  def test_rejects_spending_beyond_the_current_phase_s_unlocked_amount(self):
    escrow = build_escrow(unlock_pct=Decimal('10.00'), cap_per_acre=Decimal('5000.00'), acres=Decimal('5.00'))
    shopkeeper = UserFactory(role = 'shopkeeper')
    with pytest.raises(NotEnoughEscrowError) as exc_info:
      InputPaymentService.process_payment(escrow.id, shopkeeper, 'seed', Decimal('10000.01'))
    assert exc_info.value.available == Decimal('10000.00')

  def test_phase_cap_is_cumulative_not_reset_per_phase(self):
    loan = LoanApplicationFactory(approved_amount=Decimal('100000.00'), acres_applied_for=Decimal('5.00'))
    CropLifecycleMilestoneFactory(crop=loan.crop, phase_number=1, unlock_pct=Decimal('10.00'), allowed_input_categories=['seed'])
    CropLifecycleMilestoneFactory(crop=loan.crop, phase_number=2, unlock_pct=Decimal('10.00'), allowed_input_categories=['seed'])
    CropInputCapFactory(crop=loan.crop, district=loan.farmer.user.district, input_category='seed', valid_season=loan.crop.season, max_cost_per_acre=Decimal('10000.00'))
    escrow = EscrowCreationService.create(loan)
    EscrowCreationService.unlock_next_phase(escrow.id)  
    shopkeeper = UserFactory(role = 'shopkeeper')
    txn = InputPaymentService.process_payment(escrow.id, shopkeeper, 'seed', Decimal('15000.00'))
    assert txn.amount == Decimal('15000.00')

  def test_rejects_when_remaining_balance_is_the_binding_constraint(self):
    escrow = build_escrow(unlock_pct=Decimal('100.00'), cap_per_acre=Decimal('50000.00'), acres=Decimal('5.00'))
    escrow.remaining_balance = Decimal('500.00')
    escrow.save(update_fields=['remaining_balance'])
    shopkeeper = UserFactory(role = 'shopkeeper')
    with pytest.raises(ValueError, match = 'Insufficient escrow balance'):
      InputPaymentService.process_payment(escrow.id, shopkeeper, 'seed', Decimal('501.00'))
      
@pytest.mark.django_db
class TestInputPaymentServiceSuccessPath:
  def test_credits_the_shopkeeper_s_real_wallet(self):
    escrow = build_escrow(unlock_pct=Decimal('100.00'))
    shopkeeper = UserFactory(role = 'shopkeeper')
    balance_before = shopkeeper.wallet.balance
    InputPaymentService.process_payment(escrow.id, shopkeeper, 'seed', Decimal('500.00'))
    shopkeeper.wallet.refresh_from_db()
    assert shopkeeper.wallet.balance == balance_before + Decimal('500.00')

  def test_updates_escrow_balance_and_total_spent_together(self):
    escrow = build_escrow(unlock_pct=Decimal('100.00'))
    shopkeeper = UserFactory(role = 'shopkeeper')
    remaining_before = escrow.remaining_balance
    InputPaymentService.process_payment(escrow.id, shopkeeper, 'seed', Decimal('500.00'))
    escrow.refresh_from_db()
    assert escrow.remaining_balance == remaining_before - Decimal('500.00')
    assert escrow.total_spent_on_inputs == Decimal('500.00')

  def test_afo_cap_snapshot_is_frozen_at_transaction_time(self):
    escrow = build_escrow(unlock_pct=Decimal('100.00'), cap_per_acre=Decimal('2000.00'))
    shopkeeper = UserFactory(role='shopkeeper')
    txn = InputPaymentService.process_payment(escrow.id, shopkeeper, 'seed', Decimal('500.00'))
    assert txn.afo_cap_snapshot == Decimal('2000.00')
    CropInputCap.objects.filter(input_category='seed').update(max_cost_per_acre=Decimal('9999.00'))
    txn.refresh_from_db()
    assert txn.afo_cap_snapshot == Decimal('2000.00')

@pytest.mark.django_db
class TestInputPaymentServiceRejectionIsAtomic:
  def test_rejected_payment_leaves_escrow_and_wallet_completely_untouched(self):
    escrow = build_escrow(unlock_pct=Decimal('100.00'), cap_per_acre=Decimal('100.00'), acres=Decimal('1.00'))
    shopkeeper = UserFactory(role = 'shopkeeper')
    wallet_before = shopkeeper.wallet.balance
    remaining_before = escrow.remaining_balance
    spent_before = escrow.total_spent_on_inputs
    with pytest.raises(AFOLimitExceededError):
      InputPaymentService.process_payment(escrow.id, shopkeeper, 'seed', Decimal('999.00'))
    escrow.refresh_from_db()
    shopkeeper.wallet.refresh_from_db()
    assert escrow.remaining_balance == remaining_before
    assert escrow.total_spent_on_inputs == spent_before
    assert shopkeeper.wallet.balance == wallet_before
    assert escrow.transactions.filter(txn_type = 'input').count() == 0
    
@pytest.mark.django_db
class TestEscrowModelConstraints:

  def test_unique_together_prevents_duplicate_milestone_unlock(self):
    escrow = build_escrow()
    milestone = escrow.unlocks.first().milestone
    with pytest.raises(IntegrityError):
      EscrowMilestoneUnlock.objects.create(escrow=escrow, milestone=milestone, unlocked_amount=Decimal('1.00'), is_active=False)

  def test_escrow_wallet_deletion_is_protected_by_its_transactions(self):
    escrow = build_escrow()
    with pytest.raises(ProtectedError):
      escrow.delete()

@pytest.mark.django_db(transaction=True)
class TestInputPaymentConcurrency:

  def test_concurrent_payments_cannot_jointly_exceed_the_afo_cap(self):
    escrow = build_escrow(unlock_pct=Decimal('100.00'), cap_per_acre=Decimal('100.00'), acres=Decimal('1.00'))
    shopkeeper = UserFactory(role = 'shopkeeper')
    amount = Decimal('80.00')
    barrier = threading.Barrier(2)
    results = Queue()
    def worker():
      barrier.wait()
      try:
        InputPaymentService.process_payment(escrow.id, shopkeeper, 'seed', amount)
        results.put('success')
      except (AFOLimitExceededError, NotEnoughEscrowError, ValueError):
        results.put('failure')
      finally:
        connections.close_all()
    threads = [threading.Thread(target=worker) for _ in range(2)]
    for t in threads:
      t.start()
    for t in threads:
      t.join()
      
    outcomes = list(results.queue)
    assert outcomes.count('success') == 1, f"expected exactly one payment to succeed, got: {outcomes}"
    total_spent = EscrowTransaction.objects.filter(escrow=escrow, txn_type = 'input').aggregate(total=Sum('amount'))['total'] or Decimal('0')
    assert total_spent <= Decimal('100.00')