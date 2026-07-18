from django.test import TestCase
from rest_framework.test import APIClient
from apps.accounts.models import User
from unittest.mock import patch
from rest_framework import status
from apps.credit.models import OTPConsent, CreditCheck
 
class CreditViewsTests(TestCase):
  def setUp(self):
    self.client = APIClient()
    self.farmer = User.objects.create_user(
      phone = '03005550001', cnic = '3520355500011', full_name = 'View Test Farmer',
      password = 'pass12312', role = 'smallholder', district = 'Bahawalpur', province = 'punjab')
    self.other_farmer = User.objects.create_user(
      phone = '03005550002', cnic = '3520355500021', full_name = 'Other Farmer',
      password = 'pass12312', role = 'smallholder', district = 'Bahawalpur', province = 'punjab')
    self.bank = User.objects.create_user(
      phone = '03005550003', cnic = '3520355500031', full_name = 'Bank Manager',
      password = 'pass12312', role = 'bank', district = 'Bahawalpur', province = 'punjab')
 
  @patch('apps.credit.services.NotificationService.notify')
  def test_farmer_can_request_otp(self, mock_notify):
    self.client.force_authenticate(self.farmer)
    response = self.client.post('/credit/checks/consent-otp/', {})
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertIn('otp_reference', response.data)
 
  def test_bank_cannot_request_otp_for_a_farmer_flow(self):
    self.client.force_authenticate(self.bank)
    response = self.client.post('/credit/checks/consent-otp/', {})
    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
 
  @patch('apps.credit.services.NotificationService.notify')
  def test_verify_otp_wrong_code_returns_400(self, mock_notify):
    self.client.force_authenticate(self.farmer)
    otp_response = self.client.post('/credit/checks/consent-otp/', {})
    response = self.client.post('/credit/checks/consent-otp/verify/', {
      'otp_reference': otp_response.data['otp_reference'], 'otp_code': '000000'})
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
 
  @patch('apps.credit.services.NotificationService.notify')
  @patch('apps.credit.tasks.execute_bureau_check.delay')
  def test_trigger_without_verified_consent_returns_consent_not_verified(self, mock_delay, mock_notify):
    self.client.force_authenticate(self.farmer)
    otp_response = self.client.post('/credit/checks/consent-otp/', {})
    response = self.client.post('/credit/checks/trigger/', {'otp_reference': otp_response.data['otp_reference']})
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response.data['error'], 'CONSENT_NOT_VERIFIED')
 
  @patch('apps.credit.services.NotificationService.notify')
  def test_trigger_with_invalid_loan_id_returns_404_not_silent_none(self, mock_notify):
    self.client.force_authenticate(self.farmer)
    otp_response = self.client.post('/credit/checks/consent-otp/', {})
    otp_ref = otp_response.data['otp_reference']
    consent = OTPConsent.objects.get(id=otp_ref)
    consent.verified = True
    consent.save(update_fields=['verified'])
    response = self.client.post('/credit/checks/trigger/', {
      'otp_reference': otp_ref, 'loan_id': '11111111-1111-1111-1111-111111111111'})
    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
 
  def test_farmer_sees_only_own_checks(self):
    CreditCheck.objects.create(farmer=self.farmer.farmer_profile, cnic_number=self.farmer.cnic, status = 'completed')
    CreditCheck.objects.create(farmer=self.other_farmer.farmer_profile, cnic_number=self.other_farmer.cnic, status = 'completed')
    self.client.force_authenticate(self.farmer)
    response = self.client.get('/credit/checks/')
    self.assertEqual(response.data['count'], 1)
    
  def test_bank_sees_all_checks(self):
    CreditCheck.objects.create(farmer=self.farmer.farmer_profile, cnic_number=self.farmer.cnic, status = 'completed')
    CreditCheck.objects.create(farmer=self.other_farmer.farmer_profile, cnic_number=self.other_farmer.cnic, status = 'completed')
    self.client.force_authenticate(self.bank)
    response = self.client.get('/credit/checks/')
    self.assertEqual(response.data['count'], 2)
 
  def test_bank_retrieve_uses_detail_serializer_with_raw_response(self):
    check = CreditCheck.objects.create(
      farmer=self.farmer.farmer_profile, cnic_number=self.farmer.cnic, status = 'completed',
      raw_bank_response={'some': 'data'})
    self.client.force_authenticate(self.bank)
    response = self.client.get(f'/credit/checks/{check.id}/')
    self.assertIn('raw_bank_response', response.data)
 
  def test_farmer_retrieve_does_not_expose_raw_bank_response(self):
    check = CreditCheck.objects.create(
      farmer=self.farmer.farmer_profile, cnic_number=self.farmer.cnic, status = 'completed',
      raw_bank_response={'some': 'data'})
    self.client.force_authenticate(self.farmer)
    response = self.client.get(f'/credit/checks/{check.id}/')
    self.assertNotIn('raw_bank_response', response.data)
 
  def test_otp_verify_throttle_scope_applied(self):
    from apps.credit.views import CreditCheckViewSet
    view = CreditCheckViewSet()
    view.action = 'verify_otp'
    view.get_throttles()
    self.assertEqual(view.throttle_scope, 'otp_verify')
 