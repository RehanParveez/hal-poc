import logging
from decimal import Decimal, ROUND_DOWN
from django.db import transaction
from apps.settlements.models import SettlementInvoice
from apps.loans.models import LoanApplication
from apps.wallets.models import Wallet, WalletTransaction
from django.utils import timezone
from apps.notifications.services import NotificationService
from apps.contracts.services import CropContractService

logger = logging.getLogger(__name__)

FACTORING_COMMISSION_RATE = Decimal('0.006')
PLATFORM_FEE_RATE = Decimal('0.005')

class SettlementService:
  @staticmethod
  def execute_settlement(batch):
    loan = batch.allocation.loan
    tenant_agreement = loan.tenant_agreement
    with transaction.atomic():
      if SettlementInvoice.objects.filter(batch=batch).exists():
        raise ValueError("this batch has already been settled.")
      farmer_wallet = Wallet.objects.select_for_update().get(user=loan.farmer.user)
      loan_locked = LoanApplication.objects.select_for_update().get(id=loan.id)
      if loan_locked.approved_amount is None or loan_locked.interest_rate_pct is None:
        raise ValueError(f"Loan {loan_locked.id} is missing approved_amount or interest_rate_pct — it must be approved through the proper approval flow before settlement.")
      gross = batch.actual_payout
      batch_proportion = batch.batch_kg / batch.allocation.committed_kg
      principal = (loan_locked.approved_amount * batch_proportion).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
      if loan_locked.approved_at:
        start_date = loan_locked.approved_at.date()
      else:
        start_date = loan_locked.created_at.date()
      days_out = (timezone.now().date() - start_date).days
      interest = (principal * (loan_locked.interest_rate_pct / Decimal('100')) * days_out / Decimal('365')).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
      bank_commission = (gross * FACTORING_COMMISSION_RATE).quantize(Decimal('0.01'))
      platform_fee = Decimal('0.01')

      theka_payment = Decimal('0')
      batai_landowner_share = Decimal('0')
      landowner_wallet = None
      if tenant_agreement:
        landowner_wallet = Wallet.objects.select_for_update().get(user=tenant_agreement.parcel.landowner.user)
        sub_gross = gross - principal - interest - bank_commission - platform_fee
        if tenant_agreement.agreement_type == 'theka':
          theka_payment = (tenant_agreement.theka_amount * batch_proportion).quantize(Decimal('0.01'))
        elif tenant_agreement.agreement_type == 'batai':
          batai_landowner_share = (sub_gross * tenant_agreement.landowner_share_pct / Decimal('100')).quantize(Decimal('0.01'))
      farmer_net = (
        gross - principal - interest - bank_commission
        - platform_fee - theka_payment - batai_landowner_share)

      insurance_triggered = False
      if farmer_net < Decimal('0'):
        logger.error(f"SETTLEMENT: farmer_net < 0 ({farmer_net}) on batch {batch.id}. "
          f"the grade deduction: {batch.grade_deduction_pct}%. Insurance flag set.")
        farmer_net = Decimal('0')
        insurance_triggered = True
      invoice = SettlementInvoice.objects.create(batch=batch, loan=loan_locked, tenant_agreement=tenant_agreement, gross_payout=gross, proportional_principal_deduction=principal,
        bank_interest_deduction=interest, bank_factoring_commission=bank_commission, platform_transaction_fee=platform_fee, theka_payment=theka_payment,
        batai_landowner_share=batai_landowner_share, farmer_net_profit=farmer_net, insurance_claim_triggered=insurance_triggered, status='advanced', bank_advanced_at=timezone.now())

      if farmer_net > Decimal('0'):
        farmer_wallet.balance += farmer_net
        farmer_wallet.save(update_fields=['balance'])
        WalletTransaction.objects.create(wallet=farmer_wallet, amount=farmer_net, direction='credit',
          txn_type='farmer_profit', reference_id=invoice.id, note=f"Batch {batch.id} — {batch.grade_received}")

      if landowner_wallet:
        lo_amount = theka_payment + batai_landowner_share
        if lo_amount > Decimal('0'):
          landowner_wallet.balance += lo_amount
          landowner_wallet.save(update_fields=['balance'])
          WalletTransaction.objects.create(wallet=landowner_wallet, amount=lo_amount, direction='credit',
            txn_type='batai_split' if batai_landowner_share > 0 else 'theka_payment', reference_id=invoice.id)

      loan_locked.loan_recovered_to_date += (principal + interest)
      if loan_locked.loan_recovered_to_date >= loan_locked.approved_amount:
        loan_locked.status = 'repaid'
      loan_locked.save(update_fields=['loan_recovered_to_date', 'status'])
      batch.status = 'payment_triggered'
      batch.save(update_fields=['status'])
      CropContractService.check_and_complete_contract(batch.allocation.contract)
      transaction.on_commit(lambda: NotificationService.notify(loan.farmer.user, 'settlement_complete',
       {'batch_kg': batch.batch_kg, 'farmer_net_profit': farmer_net}, reference_id=invoice.id))

    print(f"\n{'='*60}")
    print(f"  HAL SETTLEMENT")
    print(f"{'='*60}")
    print(f"  Farmer: {loan.farmer.user.full_name}")
    print(f"  Batch: {batch.batch_kg} kg {loan.crop.name}")
    print(f"  Grade: {batch.grade_received} ({batch.grade_deduction_pct}% deduction)")
    print(f"  {'-'*40}")
    print(f"  Gross Payout: PKR {gross:>12}")
    print(f"  - Loan Principal: PKR {principal:>12}")
    print(f"  - Interest: PKR {interest:>12}")
    print(f"  - Bank Commission: PKR {bank_commission:>12}")
    if platform_fee:
      print(f"  - Platform Fee: PKR {platform_fee:>12}")
    if theka_payment:
      print(f"  - Theka Rent: PKR {theka_payment:>12}")
    if batai_landowner_share:
      print(f"  - Batai (Landowner): PKR {batai_landowner_share:>12}")
    print(f"  {'-'*40}")
    print(f"  FARMER NET PROFIT:   PKR {farmer_net:>12}")
    if insurance_triggered:
      print(f" the insurance claim is triggered")
    print(f"{'='*60}\n")

    return invoice
  
  @staticmethod
  def confirm_factory_settlement(invoice_id, factory_profile):
    with transaction.atomic():
      invoice = SettlementInvoice.objects.select_for_update().select_related('batch__allocation__contract__factory', 'loan__bank__user').get(id=invoice_id)
      if invoice.batch.allocation.contract.factory != factory_profile:
        raise PermissionError("you dont have perm to settle this invoice.")
      if invoice.status not in ['pending', 'advanced']:
        raise ValueError("this invoice has already been process. or cant be settled.")
      bank_wallet = Wallet.objects.select_for_update().get(user=invoice.loan.bank.user)
      bank_wallet.balance += invoice.gross_payout
      bank_wallet.save(update_fields=['balance'])

      WalletTransaction.objects.create(wallet=bank_wallet, amount=invoice.gross_payout, direction = 'credit', txn_type = 'settlement', reference_id=invoice.id,
        note=f"factory settlement confirmed for Batch {invoice.batch.id}")
      invoice.status = 'factsettl'
      invoice.factory_paid_at = timezone.now()
      invoice.save(update_fields=['status', 'factory_paid_at'])
      transaction.on_commit(lambda: NotificationService.notify(invoice.loan.bank.user, 'factory_settlement_confirmed',
       {'gross_payout': invoice.gross_payout}, reference_id=invoice.id))

      return invoice