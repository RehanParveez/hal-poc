from django.db import transaction
from django.utils import timezone
from apps.loans.models import LoanApplication
from shared.exceptions import LoanAlreadyDisbursedError
from apps.escrow.services import EscrowCreationService
from apps.escrow.models import EscrowWallet

class LoanApplicationService:
  @staticmethod
  def apply_for_loan(farmer_profile, bank_profile, validated_data):
    with transaction.atomic():
      loan = LoanApplication.objects.create(farmer=farmer_profile, bank=bank_profile, status='submitted', **validated_data)
      return loan

  @staticmethod
  def approve_loan(loan_id, bank_profile, approved_amount, interest_rate_pct):
    with transaction.atomic():
      loan = LoanApplication.objects.select_for_update().get(id=loan_id)
      if loan.bank != bank_profile:
        raise PermissionError("You can only approve loans assigned to your bank.")
      if loan.status != 'submitted':
        raise ValueError(f'only the submitted loans can be approv. Current status: {loan.status}.')
      if approved_amount is None or float(approved_amount) <= 0:
        raise ValueError(f"wrong approved_amount provided: {approved_amount}")
      loan.approved_amount = approved_amount
      loan.interest_rate_pct = interest_rate_pct
      loan.status = 'bank_approved'
      loan.approved_at = timezone.now()
      print(f"DEBUG: Before save, loan.approved_amount is: {loan.approved_amount}")
      loan.save()
      loan.refresh_from_db()
      print(f'DEBUG: Post-save database value is: {loan.approved_amount}')
      return loan

  @staticmethod
  def reject_loan(loan_id, bank_profile, rejection_reason):
    with transaction.atomic():
      loan = LoanApplication.objects.select_for_update().get(id=loan_id)
      if loan.bank != bank_profile:
        raise PermissionError("You can only reject loans assigned to your bank.")
      if loan.status not in ('submitted', 'bank_approved'):
        raise ValueError(f"cant reject a loan with status '{loan.status}'.")

      loan.status = 'rejected'
      loan.rejection_reason = rejection_reason
      loan.save(update_fields=['status', 'rejection_reason'])
      return loan
  
  @staticmethod
  def disburse_loan(loan_id, bank_profile):
    with transaction.atomic():
      loan = LoanApplication.objects.select_for_update().get(id=loan_id)
      if loan.bank != bank_profile:
        raise PermissionError("You can only disburse loans assigned to your bank.")
      if loan.status == 'disbursed':
        raise LoanAlreadyDisbursedError()
      if loan.status != 'bank_approved':
        raise ValueError(f"Loan must be bank_approved. Current: {loan.status}.")
      loan.status = 'disbursed'
      loan.disbursed_at = timezone.now()
      loan.save(update_fields=['status', 'disbursed_at'])
      loan.refresh_from_db() 
      escrow = EscrowWallet.objects.filter(loan=loan).first()
      if not escrow:
       escrow = EscrowCreationService.create(loan)
      return loan, escrow