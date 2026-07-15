import logging
from django.db import transaction
from apps.credit.models import CreditCheck
from apps.accounts.models import User
from apps.notifications.services import NotificationService
from celery import shared_task
from apps.credit.services import CreditBureauService
from shared.exceptions import CreditBureauRejectedError, ExternalServiceUnavailable
from django.utils import timezone as tz
from shared.circuit_breaker import credit_bureau_breaker

logger = logging.getLogger(__name__)

def _mark_manual_review(credit_check_id, notes=''):
  with transaction.atomic():
    check = CreditCheck.objects.select_for_update().select_related('farmer__user').get(id=credit_check_id)
    check.status = 'manual_review'
    if notes:
      check.bank_decision_notes = notes
    check.save(update_fields=['status', 'bank_decision_notes'] if notes else ['status'])

  admin = User.objects.filter(role='admin').first()
  if admin:
    NotificationService.notify(admin, 'credit_check_manual_review', {'farmer_name': check.farmer.user.full_name}, reference_id=check.id)
  logger.warning(f"Credit check {credit_check_id} moved to manual_review.")

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def execute_bureau_check(self, credit_check_id, payload):
  
  try:
    raw_response = credit_bureau_breaker.call(CreditBureauService._call_partner_bank_api, payload)
  except ExternalServiceUnavailable as exc:
    with transaction.atomic():
      check = CreditCheck.objects.select_for_update().get(id=credit_check_id)
      check.status = 'failed'
      check.save(update_fields=['status'])
    if self.request.retries < self.max_retries:
      raise self.retry(exc=exc)
    _mark_manual_review(credit_check_id)
    return
  except CreditBureauRejectedError as exc:
    _mark_manual_review(credit_check_id, notes=exc.message)
    return

  tasdeeq = raw_response['bureau_results']['tasdeeq_data']
  ecib = raw_response['bureau_results']['ecib_data']
  decision = raw_response['bank_decision']

  with transaction.atomic():
    check = CreditCheck.objects.select_for_update().select_related('farmer__user', 'loan_application').get(id=credit_check_id)
    check.credit_score = tasdeeq.get('credit_score')
    check.active_micro_loans_count = tasdeeq.get('active_micro_loans')
    check.total_outstanding_debt = ecib.get('total_exposure_pkr')
    check.default_history_flag = ecib.get('write_off_history', False)
    check.ecib_status = ecib.get('status', 'None').lower().replace('-', '_')
    check.is_eligible = decision.get('is_eligible')
    check.max_approved_limit_pkr = decision.get('max_approved_limit_pkr')
    check.bank_decision_notes = decision.get('notes', '')
    check.bank_reference_id = raw_response.get('response_id', '')
    check.raw_bank_response = raw_response
    check.status = 'completed'
    check.completed_at = tz.now()
    check.risk_tier = CreditBureauService._assign_risk_tier(check)
    check.save()

    check.farmer.user.credit_tier = check.risk_tier
    check.farmer.user.save(update_fields=['credit_tier'])

    if check.loan_application:
      check.loan_application.credit_check = check
      check.loan_application.credit_check_status = 'approved' if check.is_eligible else 'rejected'
      check.loan_application.save(update_fields=['credit_check', 'credit_check_status'])

  NotificationService.notify(check.farmer.user, 'credit_check_completed',
    {'eligibility_text': 'Eligible' if check.is_eligible else 'Not Eligible',
     'risk_tier': (check.risk_tier or 'unverified').replace('_', ' ').title()}, reference_id=check.id)