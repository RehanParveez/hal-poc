from django.test import TestCase
from django.test import TestCase, override_settings
from apps.accounts.models import User
from unittest.mock import patch
from apps.credit.services import CreditBureauService
from django.utils import timezone
from datetime import timedelta
from apps.credit.models import OTPConsent
from shared.exceptions import ConsentNotVerifiedError
from apps.credit.models import CreditCheck
 
class CreditBureauServiceOTPTests(TestCase):
  def setUp(self):
    self.farmer = User.objects.create_user(
      phone = '03003330001', cnic = '3520333300011', full_name = 'Credit Check Farmer',
      password = 'pass12312', role = 'smallholder', district = 'Bahawalpur', province = 'punjab')
 
  @patch('apps.credit.services.NotificationService.notify')
  def test_request_consent_otp_creates_hashed_unverified_consent(self, mock_notify):
    consent = CreditBureauService.request_consent_otp(self.farmer)
    self.assertFalse(consent.verified)
    self.assertTrue(consent.expires_at > timezone.now())
    self.assertTrue(consent.expires_at <= timezone.now() + timedelta(minutes=10, seconds=5))
    mock_notify.assert_called_once()
    sent_context = mock_notify.call_args[0][2]
    self.assertIn('otp_code', sent_context)
    self.assertEqual(len(sent_context['otp_code']), 6)
    self.assertNotEqual(sent_context['otp_code'], consent.otp_hash)
 
  @patch('apps.credit.services.NotificationService.notify')
  def test_verify_consent_otp_correct_code_succeeds(self, mock_notify):
    consent = CreditBureauService.request_consent_otp(self.farmer)
    otp_code = mock_notify.call_args[0][2]['otp_code']
    verified = CreditBureauService.verify_consent_otp(consent.id, otp_code, self.farmer)
    self.assertTrue(verified.verified)
    self.assertIsNotNone(verified.verified_at)
 
  @patch('apps.credit.services.NotificationService.notify')
  def test_verify_consent_otp_wrong_code_fails_and_does_not_verify(self, mock_notify):
    consent = CreditBureauService.request_consent_otp(self.farmer)
    with self.assertRaises(ValueError):
      CreditBureauService.verify_consent_otp(consent.id, '000000', self.farmer)
    consent.refresh_from_db()
    self.assertFalse(consent.verified)
 
  @patch('apps.credit.services.NotificationService.notify')
  def test_verify_consent_otp_expired_fails(self, mock_notify):
    consent = CreditBureauService.request_consent_otp(self.farmer)
    otp_code = mock_notify.call_args[0][2]['otp_code']
    OTPConsent.objects.filter(id=consent.id).update(expires_at=timezone.now() - timedelta(seconds=1))
    with self.assertRaises(ValueError):
      CreditBureauService.verify_consent_otp(consent.id, otp_code, self.farmer)
 
@override_settings(CELERY_BROKER_URL='redis://localhost:6379/0')
class CreditBureauServiceCreditCheckTests(TestCase):
  def setUp(self):
    self.farmer = User.objects.create_user(
      phone = '03003330002', cnic = '3520333300021', full_name = 'Credit Test Farmer 2',
      password = 'pass123', role = 'smallholder', district = 'Bahawalpur', province = 'punjab')
 
  @patch('apps.credit.services.NotificationService.notify')
  def test_run_credit_check_requires_verified_consent(self, mock_notify):
    consent = CreditBureauService.request_consent_otp(self.farmer)
    with self.assertRaises(ConsentNotVerifiedError):
      CreditBureauService.run_credit_check(self.farmer.farmer_profile, consent.id)
 
  @patch('apps.credit.services.NotificationService.notify')
  @patch('apps.credit.tasks.execute_bureau_check.delay')
  def test_run_credit_check_dispatches_task_when_consent_verified(self, mock_delay, mock_notify):
    consent = CreditBureauService.request_consent_otp(self.farmer)
    otp_code = mock_notify.call_args[0][2]['otp_code']
    CreditBureauService.verify_consent_otp(consent.id, otp_code, self.farmer)
    check = CreditBureauService.run_credit_check(self.farmer.farmer_profile, consent.id)
    self.assertEqual(check.status, 'pending')
    mock_delay.assert_called_once()
 
class RiskTierAssignmentTests(TestCase):
  def _check(self, **kwargs):
    defaults = {'ecib_status': 'regular', 'default_history_flag': False,
      'credit_score': None, 'active_micro_loans_count': None}
    defaults.update(kwargs)
    return CreditCheck(**defaults)
 
  def test_score_399_is_high_risk(self):
    self.assertEqual(CreditBureauService._assign_risk_tier(self._check(credit_score=399)), 'high_risk')
 
  def test_score_400_is_medium_risk(self):
    self.assertEqual(CreditBureauService._assign_risk_tier(self._check(credit_score=400)), 'medium_risk')
 
  def test_score_599_is_medium_risk(self):
    self.assertEqual(CreditBureauService._assign_risk_tier(self._check(credit_score=599)), 'medium_risk')
 
  def test_score_600_is_low_risk(self):
    self.assertEqual(CreditBureauService._assign_risk_tier(
      self._check(credit_score=600, active_micro_loans_count=0)), 'low_risk')
 
  def test_write_off_forces_high_risk_regardless_of_score(self):
    self.assertEqual(CreditBureauService._assign_risk_tier(
      self._check(credit_score=900, ecib_status = 'write_off')), 'high_risk')
 
  def test_default_history_forces_high_risk_regardless_of_score(self):
    self.assertEqual(CreditBureauService._assign_risk_tier(
      self._check(credit_score=900, default_history_flag=True)), 'high_risk')
 
  def test_two_or_more_active_loans_forces_medium_even_with_excellent_score(self):
    self.assertEqual(CreditBureauService._assign_risk_tier(
      self._check(credit_score=900, active_micro_loans_count=2)), 'medium_risk')
 
  def test_ecib_none_with_good_score_is_low_risk(self):
    result = CreditBureauService._assign_risk_tier(
      self._check(credit_score=750, ecib_status = 'none', active_micro_loans_count=0))
    self.assertEqual(result, 'low_risk')
 
  def test_ecib_none_with_midrange_score_is_medium_risk(self):
    result = CreditBureauService._assign_risk_tier(
      self._check(credit_score=500, ecib_status = 'none', active_micro_loans_count=0))
    self.assertEqual(result, 'medium_risk')
 
  def test_ecib_overdue_with_good_score_is_still_high_risk(self):
    result = CreditBureauService._assign_risk_tier(self._check(credit_score=750, ecib_status = 'overdue'))
    self.assertEqual(result, 'high_risk')
 
  def test_no_score_at_all_falls_through_to_unverified(self):
    self.assertEqual(CreditBureauService._assign_risk_tier(self._check(credit_score=None)), 'unverified')
 
class MockBureauResponseTests(TestCase):
  def test_deterministic_same_cnic_same_score(self):
    payload = {'request_id': 'abc', 'applicant_details': {'cnic': '3520212345671'}}
    r1 = CreditBureauService._mock_bureau_response(payload)
    r2 = CreditBureauService._mock_bureau_response(payload)
    self.assertEqual(
      r1['bureau_results']['tasdeeq_data']['credit_score'],
      r2['bureau_results']['tasdeeq_data']['credit_score'])