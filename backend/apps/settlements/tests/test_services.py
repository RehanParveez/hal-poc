import threading
from decimal import Decimal, ROUND_DOWN
from queue import Queue
import pytest
from django.db import connections, transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from apps.accounts.tests.factories import UserFactory, FarmerProfileFactory, BankProfileFactory, FactoryProfileFactory, LandownerProfileFactory
from apps.escrow.tests.factories import LoanApplicationFactory
from apps.contracts.tests.factories import CropContractFactory, FarmerContractAllocationFactory
from apps.delivery.tests.factories import BatchDeliveryFactory
from apps.land.tests.factories import TenantAgreementFactory, LandParcelFactory
from apps.settlements.services import SettlementService
from apps.wallets.models import Wallet, WalletTransaction

def setup_settlement_environment(agreement_type=None, approved_amount=Decimal('500000.00'),
  interest_rate=Decimal('12.50'), committed_kg=Decimal('10000.00'), batch_kg=Decimal('2500.00'), actual_payout=Decimal('180000.00'),
  days_out=45):
  farmer_user = UserFactory(role = 'smallholder')
  farmer = FarmerProfileFactory(user=farmer_user)
  bank_user = UserFactory(role = 'bank')
  bank = BankProfileFactory(user=bank_user) 
  factory_user = UserFactory(role = 'factory')
  factory = FactoryProfileFactory(user=factory_user)
  
  Wallet.objects.get_or_create(wallet_type = 'platform', defaults={'balance': Decimal('0.00')})
  Wallet.objects.get_or_create(user=farmer_user, defaults={'balance': Decimal('0.00')})
  Wallet.objects.get_or_create(user=bank_user, defaults={'balance': Decimal('0.00')})

  tenant_agreement = None
  if agreement_type:
    landowner_user = UserFactory(role = 'landowner')
    landowner = LandownerProfileFactory(user=landowner_user)
    Wallet.objects.get_or_create(user=landowner_user, defaults={'balance': Decimal('0.00')})
    parcel = LandParcelFactory(landowner=landowner)
    tenant_agreement = TenantAgreementFactory(parcel=parcel, tenant=farmer, agreement_type=agreement_type,
      theka_amount=Decimal('40000.00') if agreement_type == 'theka' else Decimal('0.00'),
      landowner_share_pct=Decimal('20.00') if agreement_type == 'batai' else Decimal('0.00'))

  approved_at_time = timezone.now() - timezone.timedelta(days=days_out)
  loan = LoanApplicationFactory(farmer=farmer, bank=bank, approved_amount=approved_amount, interest_rate_pct=interest_rate,
    approved_at=approved_at_time, tenant_agreement=tenant_agreement, loan_recovered_to_date=Decimal('0.00'),
    status = 'disbursed')
  contract = CropContractFactory(factory=factory, crop=loan.crop)
  allocation = FarmerContractAllocationFactory(contract=contract, farmer=farmer, loan=loan, committed_kg=committed_kg)
  batch = BatchDeliveryFactory(allocation=allocation, batch_kg=batch_kg, actual_payout=actual_payout,
    status = 'grade_confirmed')
  return batch, loan, tenant_agreement

@pytest.mark.django_db
class TestSettlementServiceExecuteCalculations:

  def test_execute_settlement_math_precision_and_ledger_distribution(self):
    batch, loan, _ = setup_settlement_environment(agreement_type=None, approved_amount=Decimal('100000.00'),
      interest_rate=Decimal('10.00'), committed_kg=Decimal('10000.00'), batch_kg=Decimal('2500.00'),
      actual_payout=Decimal('150000.00'), days_out=73)
    invoice = SettlementService.execute_settlement(batch)
    assert invoice.proportional_principal_deduction == Decimal('25000.00')
    assert invoice.bank_interest_deduction == Decimal('500.00')
    assert invoice.bank_factoring_commission == Decimal('900.00')
    assert invoice.platform_transaction_fee == Decimal('750.00')
    assert invoice.farmer_net_profit == Decimal('122850.00')
    assert invoice.insurance_claim_triggered is False
    assert invoice.status == 'advanced'
    assert Wallet.objects.get(user=loan.farmer.user).balance == Decimal('122850.00')
    assert Wallet.objects.get(wallet_type = 'platform').balance == Decimal('750.00')
    loan.refresh_from_db()
    assert loan.loan_recovered_to_date == Decimal('25500.00') 
    batch.refresh_from_db()
    assert batch.status == 'payment_triggered'

  def test_theka_fixed_rent_deduction_and_distribution(self):
    batch, loan, agreement = setup_settlement_environment(agreement_type = 'theka', approved_amount=Decimal('100000.00'),
      interest_rate=Decimal('0.00'), committed_kg=Decimal('10000.00'), batch_kg=Decimal('2500.00'),
      actual_payout=Decimal('100000.00'), days_out=30)
    invoice = SettlementService.execute_settlement(batch)
    assert invoice.theka_payment == Decimal('10000.00')
    assert invoice.batai_landowner_share == Decimal('0.00')
    landowner_user = agreement.parcel.landowner.user
    assert Wallet.objects.get(user=landowner_user).balance == Decimal('10000.00')
    assert WalletTransaction.objects.filter(wallet__user=landowner_user, txn_type='theka_payment').exists()

  def test_batai_sharecropping_yield_split(self):
    batch, loan, agreement = setup_settlement_environment(agreement_type = 'batai', approved_amount=Decimal('100000.00'),
      interest_rate=Decimal('0.00'), committed_kg=Decimal('10000.00'), batch_kg=Decimal('2500.00'),
      actual_payout=Decimal('100000.00'), days_out=30)
    invoice = SettlementService.execute_settlement(batch)
    assert invoice.theka_payment == Decimal('0.00')
    assert invoice.batai_landowner_share == Decimal('14780.00')
    assert invoice.farmer_net_profit == Decimal('59120.00')
    landowner_user = agreement.parcel.landowner.user
    assert Wallet.objects.get(user=landowner_user).balance == Decimal('14780.00')
    assert WalletTransaction.objects.filter(wallet__user=landowner_user, txn_type='batai_split').exists()

  def test_downside_insurance_trigger_caps_farmer_loss_at_zero(self):
    batch, loan, _ = setup_settlement_environment(agreement_type=None, approved_amount=Decimal('400000.00'),
      interest_rate=Decimal('10.00'), committed_kg=Decimal('10000.00'), batch_kg=Decimal('2500.00'), actual_payout=Decimal('20000.00'), 
      days_out=365)
    invoice = SettlementService.execute_settlement(batch)
    assert invoice.farmer_net_profit == Decimal('0.00')
    assert invoice.insurance_claim_triggered is True
    assert Wallet.objects.get(user=loan.farmer.user).balance == Decimal('0.00')

  def test_loan_lifecycle_closes_and_marks_repaid_at_limit(self):
    batch, loan, _ = setup_settlement_environment(agreement_type=None, approved_amount=Decimal('100000.00'),
      committed_kg=Decimal('10000.00'), batch_kg=Decimal('10000.00'), actual_payout=Decimal('200000.00'))
    loan.loan_recovered_to_date = Decimal('5000.00')
    loan.save()
    invoice = SettlementService.execute_settlement(batch)
    loan.refresh_from_db()
    assert loan.status == 'repaid'

@pytest.mark.django_db
class TestSettlementServiceGuardrailsAndFailures:

  def test_cannot_settle_same_batch_twice(self):
    batch, _, _ = setup_settlement_environment()
    SettlementService.execute_settlement(batch)
    with pytest.raises(ValueError, match="this batch has already been settled"):
      SettlementService.execute_settlement(batch)

  def test_unapproved_or_misconfigured_loans_are_rejected(self):
    batch, loan, _ = setup_settlement_environment()
    loan.approved_amount = None
    loan.save()
    with pytest.raises(ValueError, match = "missing approved_amount or interest_rate_pct"):
      SettlementService.execute_settlement(batch)

@pytest.mark.django_db
class TestFactorySettlementConfirmationPipeline:

  def test_authorized_factory_can_confirm_settlement(self):
    batch, loan, _ = setup_settlement_environment()
    invoice = SettlementService.execute_settlement(batch)
    factory_profile = batch.allocation.contract.factory
    bank_wallet = Wallet.objects.get(user=loan.bank.user)
    initial_bank_balance = bank_wallet.balance
    confirmed_invoice = SettlementService.confirm_factory_settlement(invoice.id, factory_profile)
    assert confirmed_invoice.status == 'factsettl'
    assert confirmed_invoice.factory_paid_at is not None
    bank_wallet.refresh_from_db()
    assert bank_wallet.balance == initial_bank_balance + invoice.gross_payout

  def test_unauthorized_factory_raises_permission_error(self):
    batch, _, _ = setup_settlement_environment()
    invoice = SettlementService.execute_settlement(batch)
    rogue_factory_user = UserFactory(role = 'factory')
    rogue_factory = FactoryProfileFactory(user=rogue_factory_user)

    with pytest.raises(PermissionError, match = "you dont have perm to settle this invoice"):
      SettlementService.confirm_factory_settlement(invoice.id, rogue_factory)

  def test_cannot_confirm_already_processed_invoice(self):
    batch, _, _ = setup_settlement_environment()
    invoice = SettlementService.execute_settlement(batch)
    factory_profile = batch.allocation.contract.factory
    SettlementService.confirm_factory_settlement(invoice.id, factory_profile)
    with pytest.raises(ValueError, match = "this invoice has already been process"):
      SettlementService.confirm_factory_settlement(invoice.id, factory_profile)

@pytest.mark.django_db(transaction=True)
class TestSettlementConcurrencySafety:

  def test_concurrent_settlement_calls_cannot_double_credit_wallets(self):
    batch, _, _ = setup_settlement_environment()
    barrier = threading.Barrier(2)
    execution_results = Queue()

    def worker_thread():
      connections.close_all()
      barrier.wait()
      try:
        with transaction.atomic():
          SettlementService.execute_settlement(batch)
        execution_results.put("SUCCESS")
      except ValueError as ex:
        execution_results.put(f"VALUE_ERROR: {str(ex)}")
      except Exception as ex:
        execution_results.put(f"FAIL: {type(ex).__name__}: {str(ex)}")
      finally:
        connections.close_all()

    threads = [threading.Thread(target=worker_thread) for _ in range(2)]
    for t in threads:
      t.start()
    for t in threads:
      t.join()
    outcomes = list(execution_results.queue)
    assert outcomes.count("SUCCESS") == 1
    assert any("this batch has already been settled" in text or 
      "IntegrityError" in text or 
      "OperationalError" in text 
      for text in outcomes)