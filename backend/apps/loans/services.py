from django.db import transaction
from django.utils import timezone
from apps.loans.models import LoanApplication

class LoanApplicationService:
  @staticmethod
  def apply_for_loan(farmer_profile, bank_profile, validated_data):
    from .models import LoanApplication
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

      loan.approved_amount = approved_amount
      loan.interest_rate_pct = interest_rate_pct
      loan.status = 'bank_approved'
      loan.approved_at = timezone.now()
      loan.save(update_fields=['approved_amount', 'interest_rate_pct', 'status', 'approved_at'])
      return loan

  @staticmethod
  def reject_loan(loan_id, bank_profile, rejection_reason):
    from .models import LoanApplication
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