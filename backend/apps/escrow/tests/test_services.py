from decimal import Decimal
import pytest
from apps.escrow.models import EscrowWallet, EscrowMilestoneUnlock
from apps.escrow.services import EscrowCreationService
from apps.escrow.tests.factories import LoanApplicationFactory, CropLifecycleMilestoneFactory, CropInputCapFactory

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