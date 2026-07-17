from django.test import TestCase
from apps.accounts.models import User
from unittest.mock import patch
from apps.community.services import NumberdarVerificationService
from shared.exceptions import OutOfJurisdictionError, DuplicateVerificationRequestError
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
from apps.community.models import FarmerVerificationRequest

class NumberdarVerificationServiceTests(TestCase):
  def setUp(self):
    self.farmer_user = User.objects.create_user(
      phone = '03001110001', cnic = '3520211100011', full_name = 'check Farmer',
      password = 'pass12312', role = 'smallholder', district = 'Bahawalpur', province = 'punjab')
    self.other_district_farmer = User.objects.create_user(
      phone = '03001110002', cnic = '3520211100021', full_name = 'Other District Farmer',
      password = 'pass123', role = 'smallholder', district = 'Multan', province = 'punjab')
    self.numberdar_user = User.objects.create_user(
      phone = '03001110003', cnic = '3520211100031', full_name = 'check numberdar',
      password = 'pass12312', role = 'numberdar', district = 'Bahawalpur', province = 'punjab')
    self.numberdar_user.numberdar_profile.jurisdiction_district = 'Bahawalpur'
    self.numberdar_user.numberdar_profile.is_active = True
    self.numberdar_user.numberdar_profile.save()

    self.other_numberdar_user = User.objects.create_user(
      phone = '03001110004', cnic = '3520211100041', full_name = 'Other Numberdar',
      password = 'pass123', role = 'numberdar', district = 'Bahawalpur', province = 'punjab')
    self.other_numberdar_user.numberdar_profile.jurisdiction_district = 'Bahawalpur'
    self.other_numberdar_user.numberdar_profile.is_active = True
    self.other_numberdar_user.numberdar_profile.save()

  @patch('apps.community.services.NotificationService.notify')
  def test_submit_verification_request_success(self, mock_notify):
    with self.captureOnCommitCallbacks(execute=True):
      req = NumberdarVerificationService.submit_verification_request(
        self.farmer_user.farmer_profile, 
        self.numberdar_user.numberdar_profile.id
      )
    self.assertEqual(req.status, 'pending')
    self.assertEqual(req.numberdar, self.numberdar_user.numberdar_profile)
    mock_notify.assert_called_once()

  def test_submit_verification_request_out_of_jurisdiction(self):
    with self.assertRaises(OutOfJurisdictionError):
      NumberdarVerificationService.submit_verification_request(
        self.other_district_farmer.farmer_profile, self.numberdar_user.numberdar_profile.id)

  @patch('apps.community.services.NotificationService.notify')
  def test_submit_verification_request_duplicate_pending_blocked(self, mock_notify):
    NumberdarVerificationService.submit_verification_request(
      self.farmer_user.farmer_profile, self.numberdar_user.numberdar_profile.id)
    with self.assertRaises(DuplicateVerificationRequestError):
     NumberdarVerificationService.submit_verification_request(
      self.farmer_user.farmer_profile, self.numberdar_user.numberdar_profile.id)

  @patch('apps.community.services.NotificationService.notify')
  def test_submit_verification_request_duplicate_approved_blocked(self, mock_notify):
    req = NumberdarVerificationService.submit_verification_request(
      self.farmer_user.farmer_profile, self.numberdar_user.numberdar_profile.id)
    NumberdarVerificationService.approve_farmer(req.id, self.numberdar_user)
    with self.assertRaises(DuplicateVerificationRequestError):
      NumberdarVerificationService.submit_verification_request(
       self.farmer_user.farmer_profile, self.numberdar_user.numberdar_profile.id)

  def test_duplicate_request_blocked_at_database_level_even_if_app_check_bypassed(self):
    FarmerVerificationRequest.objects.create(
      farmer=self.farmer_user.farmer_profile, numberdar=self.numberdar_user.numberdar_profile, status = 'pending')
    with self.assertRaises(IntegrityError):
      FarmerVerificationRequest.objects.create(
        farmer=self.farmer_user.farmer_profile, numberdar=self.other_numberdar_user.numberdar_profile, status = 'pending')

  @patch('apps.community.services.NotificationService.notify')
  def test_approve_farmer_success(self, mock_notify):
    req = NumberdarVerificationService.submit_verification_request(
      self.farmer_user.farmer_profile, self.numberdar_user.numberdar_profile.id)
    NumberdarVerificationService.approve_farmer(req.id, self.numberdar_user)

    req.refresh_from_db()
    self.farmer_user.refresh_from_db()
    self.numberdar_user.numberdar_profile.refresh_from_db()

    self.assertEqual(req.status, 'approved')
    self.assertTrue(self.farmer_user.numberdar_verified)
    self.assertEqual(self.numberdar_user.numberdar_profile.total_farmers_verified, 1)

  @patch('apps.community.services.NotificationService.notify')
  def test_approve_farmer_wrong_numberdar_denied(self, mock_notify):
    req = NumberdarVerificationService.submit_verification_request(
      self.farmer_user.farmer_profile, self.numberdar_user.numberdar_profile.id)
    with self.assertRaises(PermissionError):
      NumberdarVerificationService.approve_farmer(req.id, self.other_numberdar_user)

  @patch('apps.community.services.NotificationService.notify')
  def test_approve_farmer_already_resolved_raises(self, mock_notify):
    req = NumberdarVerificationService.submit_verification_request(
      self.farmer_user.farmer_profile, self.numberdar_user.numberdar_profile.id)
    NumberdarVerificationService.approve_farmer(req.id, self.numberdar_user)
    with self.assertRaises(ValueError):
      NumberdarVerificationService.approve_farmer(req.id, self.numberdar_user)

  @patch('apps.community.services.NotificationService.notify')
  def test_numberdar_counter_increments_correctly_across_multiple_approvals(self, mock_notify):
    farmer_2 = User.objects.create_user(
      phone = '03001110005', cnic = '3520211100051', full_name = 'Second Farmer',
      password = 'pass123', role = 'smallholder', district = 'Bahawalpur', province = 'punjab')
    req1 = NumberdarVerificationService.submit_verification_request(
      self.farmer_user.farmer_profile, self.numberdar_user.numberdar_profile.id)
    req2 = NumberdarVerificationService.submit_verification_request(
      farmer_2.farmer_profile, self.numberdar_user.numberdar_profile.id)
    NumberdarVerificationService.approve_farmer(req1.id, self.numberdar_user)
    NumberdarVerificationService.approve_farmer(req2.id, self.numberdar_user)

    self.numberdar_user.numberdar_profile.refresh_from_db()
    self.assertEqual(self.numberdar_user.numberdar_profile.total_farmers_verified, 2)

  @patch('apps.community.services.NotificationService.notify')
  def test_reject_farmer_success(self, mock_notify):
    req = NumberdarVerificationService.submit_verification_request(
      self.farmer_user.farmer_profile, self.numberdar_user.numberdar_profile.id)
    rejected = NumberdarVerificationService.reject_farmer(req.id, self.numberdar_user, notes='CNIC mismatch')

    self.assertEqual(rejected.status, 'rejected')
    self.assertEqual(rejected.numberdar_notes, 'CNIC mismatch')
    self.farmer_user.refresh_from_db()
    self.assertFalse(self.farmer_user.numberdar_verified)

  @patch('apps.community.services.NotificationService.notify')
  def test_reject_farmer_wrong_numberdar_denied(self, mock_notify):
    req = NumberdarVerificationService.submit_verification_request(
      self.farmer_user.farmer_profile, self.numberdar_user.numberdar_profile.id)
    with self.assertRaises(PermissionError):
      NumberdarVerificationService.reject_farmer(req.id, self.other_numberdar_user)

  @patch('apps.community.services.NotificationService.notify')
  def test_escalate_timed_out_requests(self, mock_notify):
    admin = User.objects.create_user(
      phone = '03001110006', cnic = '3520211100061', full_name = 'Admin',
      password = 'pass12312', role = 'admin', district = 'Bahawalpur', province = 'punjab')
    req = NumberdarVerificationService.submit_verification_request(
      self.farmer_user.farmer_profile, self.numberdar_user.numberdar_profile.id)
    FarmerVerificationRequest.objects.filter(id=req.id).update(
      submitted_at=timezone.now() - timedelta(days=8))

    count = NumberdarVerificationService.escalate_timed_out_requests()
    req.refresh_from_db()
    self.assertEqual(count, 1)
    self.assertEqual(req.status, 'escalated')
    self.assertEqual(req.escalated_to, admin)

  @patch('apps.community.services.NotificationService.notify')
  def test_escalate_does_not_touch_recent_requests(self, mock_notify):
    NumberdarVerificationService.submit_verification_request(
      self.farmer_user.farmer_profile, self.numberdar_user.numberdar_profile.id)
    count = NumberdarVerificationService.escalate_timed_out_requests()
    self.assertEqual(count, 0)