import logging
import secrets
import bcrypt
from django.db import transaction
from apps.credit.models import OTPConsent, CreditCheck
from apps.notifications.services import NotificationService
from shared.exceptions import ConsentNotVerifiedError, CreditBureauRejectedError, ExternalServiceUnavailable
from django.utils import timezone
import hashlib
import json
from django.conf import settings

logger = logging.getLogger(__name__)
OTP_EXPIRY_MINUTES = 10

class CreditBureauService:

  @staticmethod
  def request_consent_otp(farmer_user):
    otp_code = f"{secrets.randbelow(1000000):06d}"
    otp_hash = bcrypt.hashpw(otp_code.encode(), bcrypt.gensalt()).decode()
    with transaction.atomic():
      consent = OTPConsent.objects.create(
        user=farmer_user, purpose = 'credit_check', phone_sent_to=farmer_user.phone,
        otp_hash=otp_hash, verified=False, expires_at=timezone.now() + timezone.timedelta(minutes=OTP_EXPIRY_MINUTES))

    NotificationService.notify(farmer_user, 'credit_otp_sent', {'otp_code': otp_code}, reference_id=consent.id)
    return consent

  @staticmethod
  def verify_consent_otp(otp_reference, submitted_otp, farmer_user):
    with transaction.atomic():
      consent = OTPConsent.objects.select_for_update().get(id=otp_reference, user=farmer_user, purpose = 'credit_check')
      if timezone.now() > consent.expires_at:
        raise ValueError("this otp has expired. please request a new one.")
      if not bcrypt.checkpw(submitted_otp.encode(), consent.otp_hash.encode()):
        raise ValueError('wrong otp. Please try again.')
      consent.verified = True
      consent.verified_at = timezone.now()
      consent.save(update_fields=['verified', 'verified_at'])
    return consent

  @staticmethod
  def run_credit_check(farmer_profile, otp_reference, loan_application=None):
    consent = OTPConsent.objects.get(id=otp_reference, user=farmer_profile.user, purpose = 'credit_check')
    if not consent.verified:
      raise ConsentNotVerifiedError()

    payload = {
      'platform_id': settings.PARTNER_BANK_PLATFORM_ID,
      'applicant_details': {
        'farmer_id': str(farmer_profile.user.id), 'cnic': farmer_profile.user.cnic,
        'full_name': farmer_profile.user.full_name, 'phone_number': farmer_profile.user.phone,
      },
      'loan_details': {
        'requested_amount_pkr': str(loan_application.requested_amount) if loan_application else None,
        'loan_purpose': 'Agricultural Input Financing',
      },
      'legal_compliance': {
        'consent_given': True, 'consent_timestamp': consent.verified_at.isoformat(),
        'consent_method': 'OTP_Digital_Signature', 'otp_reference': str(consent.id),
      },
    }
    payload_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    with transaction.atomic():
      check = CreditCheck.objects.create(
        farmer=farmer_profile, loan_application=loan_application, cnic_number=farmer_profile.user.cnic,
        status='pending', consent_timestamp=consent.verified_at, otp_reference=consent.id, request_payload_hash=payload_hash)

    payload['request_id'] = str(check.id)
    from apps.credit.tasks import execute_bureau_check
    execute_bureau_check.delay(str(check.id), payload)
    return check

  @staticmethod
  def _call_partner_bank_api(payload):
    if not settings.PARTNER_BANK_API_URL or settings.PARTNER_BANK_API_URL == 'MOCK':
      return CreditBureauService._mock_bureau_response(payload)

    import requests
    response = requests.post(
      f"{settings.PARTNER_BANK_API_URL}/bureau/check", json=payload,
      headers={'X-Platform-ID': settings.PARTNER_BANK_PLATFORM_ID, 'Authorization': f'Bearer {settings.PARTNER_BANK_API_KEY}'},
      timeout=30)
    if response.status_code >= 500:
      raise ExternalServiceUnavailable(service_name = 'partner bank bureau API')
    if response.status_code >= 400:
      raise CreditBureauRejectedError(response.json().get('message', 'Bureau request rejected.'))
    return response.json()

  @staticmethod
  def _mock_bureau_response(payload):
    cnic = payload['applicant_details']['cnic']
    score = 300 + (sum(int(d) for d in cnic if d.isdigit()) * 17) % 700
    return {
      'response_id': f"MOCK-{payload['request_id']}", 'timestamp': timezone.now().isoformat(), 'status': 'SUCCESS',
      'bureau_results': {
        'tasdeeq_data': {'match_found': True, 'credit_score': score, 'active_micro_loans': score % 3, 'past_defaults': 0},
        'ecib_data': {'match_found': True, 'total_exposure_pkr': 0, 'write_off_history': False, 'status': 'Regular'},
      },
      'bank_decision': {
        'is_eligible': score >= 400,
        'max_approved_limit_pkr': 100000 if score >= 600 else (50000 if score >= 400 else 0),
        'notes': 'Mock response — no live partner bank sandbox configured yet.',
      },
    }

  @staticmethod
  def _assign_risk_tier(check):
    if check.ecib_status in ('overdue', 'write_off') or check.default_history_flag or (check.credit_score is not None and check.credit_score < 400):
      return 'high_risk'
    if (check.ecib_status == 'regular' and check.credit_score is not None and 400 <= check.credit_score <= 599) \
        or (check.active_micro_loans_count is not None and check.active_micro_loans_count >= 2):
      return 'medium_risk'
    if check.ecib_status == 'regular' and check.credit_score is not None and check.credit_score >= 600 \
        and (check.active_micro_loans_count or 0) <= 1 and not check.default_history_flag:
      return 'low_risk'
    return 'unverified'