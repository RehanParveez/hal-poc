from celery import shared_task
from apps.community.services import NumberdarVerificationService

@shared_task
def escalate_timed_out_verification_requests():
  return NumberdarVerificationService.escalate_timed_out_requests()