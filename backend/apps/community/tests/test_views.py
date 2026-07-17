from django.test import TestCase
from rest_framework.test import APIClient
from apps.accounts.models import User
from unittest.mock import patch
from rest_framework import status
from apps.community.models import FarmerVerificationRequest
from apps.community.views import FarmerVerificationRequestViewSet

class CommunityViewsTests(TestCase):
  def setUp(self):
    self.client = APIClient()
    self.farmer = User.objects.create_user(
      phone = '03002220001', cnic = '3520222200011', full_name = 'Farmer A',
      password = 'pass12312', role = 'smallholder', district = 'Bahawalpur', province = 'punjab')
    self.bank = User.objects.create_user(phone = '03002220002', cnic = '3520222200021', full_name = 'Bank Manager',
      password = 'pass12312', role = 'bank', district = 'Bahawalpur', province = 'punjab')
    self.numberdar = User.objects.create_user(
      phone = '03002220003', cnic = '3520222200031', full_name = 'Numberdar A',
      password = 'pass123', role = 'numberdar', district = 'Bahawalpur', province = 'punjab')
    self.numberdar.numberdar_profile.jurisdiction_district = 'Bahawalpur'
    self.numberdar.numberdar_profile.is_active = True
    self.numberdar.numberdar_profile.save()
    self.other_numberdar = User.objects.create_user(
      phone = '03002220004', cnic = '3520222200041', full_name = 'Numberdar B',
      password = 'pass12312', role = 'numberdar', district = 'Bahawalpur', province = 'punjab')
    self.other_numberdar.numberdar_profile.jurisdiction_district = 'Bahawalpur'
    self.other_numberdar.numberdar_profile.is_active = True
    self.other_numberdar.numberdar_profile.save()

  @patch('apps.community.services.NotificationService.notify')
  def test_farmer_can_submit_verification_request(self, mock_notify):
    self.client.force_authenticate(self.farmer)
    response = self.client.post('/community/verification-requests/', {'numberdar_id': str(self.numberdar.numberdar_profile.id)})
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertEqual(FarmerVerificationRequest.objects.count(), 1)

  def test_bank_cannot_submit_verification_request(self):
    self.client.force_authenticate(self.bank)
    response = self.client.post('/community/verification-requests/', {'numberdar_id': str(self.numberdar.numberdar_profile.id)})
    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

  def test_unauthenticated_request_rejected(self):
    response = self.client.post('/community/verification-requests/', {'numberdar_id': str(self.numberdar.numberdar_profile.id)})
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

  @patch('apps.community.services.NotificationService.notify')
  def test_numberdar_queue_only_shows_own_requests(self, mock_notify):
    FarmerVerificationRequest.objects.create(
      farmer=self.farmer.farmer_profile, numberdar=self.numberdar.numberdar_profile, status = 'pending')

    self.client.force_authenticate(self.other_numberdar)
    response = self.client.get('/community/verification-requests/')
    self.assertEqual(len(response.data['results']), 0)

    self.client.force_authenticate(self.numberdar)
    response = self.client.get('/community/verification-requests/')
    self.assertEqual(len(response.data['results']), 1)

  @patch('apps.community.services.NotificationService.notify')
  def test_numberdar_can_approve_own_request(self, mock_notify):
    req = FarmerVerificationRequest.objects.create(
      farmer=self.farmer.farmer_profile, numberdar=self.numberdar.numberdar_profile, status = 'pending')
    self.client.force_authenticate(self.numberdar)
    response = self.client.patch(f'/community/verification-requests/{req.id}/approve/')
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    req.refresh_from_db()
    self.assertEqual(req.status, 'approved')

  @patch('apps.community.services.NotificationService.notify')
  def test_numberdar_cannot_approve_someone_elses_request(self, mock_notify):
    req = FarmerVerificationRequest.objects.create(
      farmer=self.farmer.farmer_profile, numberdar=self.numberdar.numberdar_profile, status = 'pending')
    self.client.force_authenticate(self.other_numberdar)
    response = self.client.patch(f'/community/verification-requests/{req.id}/approve/')
    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    req.refresh_from_db()
    self.assertEqual(req.status, 'pending')

  def test_farmer_sees_only_own_requests(self):
    other_farmer = User.objects.create_user(phone = '03002220005', cnic = '3520222200051', full_name = 'Farmer B',
      password = 'pass123', role = 'smallholder', district = 'Bahawalpur', province = 'punjab')
    FarmerVerificationRequest.objects.create(farmer=self.farmer.farmer_profile, numberdar=self.numberdar.numberdar_profile, status = 'pending')
    FarmerVerificationRequest.objects.create(farmer=other_farmer.farmer_profile, numberdar=self.numberdar.numberdar_profile, status = 'pending')

    self.client.force_authenticate(self.farmer)
    response = self.client.get('/community/verification-requests/')
    self.assertEqual(len(response.data['results']), 1)

  def test_numberdar_action_throttle_scope_applied(self):
    view = FarmerVerificationRequestViewSet()
    view.action = 'approve'
    view.get_throttles()
    self.assertEqual(view.throttle_scope, 'numberdar_action')

  def test_numberdars_list_filterable_by_district(self):
    self.client.force_authenticate(self.farmer)
    response = self.client.get('/community/numberdars/', {'district': 'Bahawalpur'})
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(len(response.data['results']), 2)