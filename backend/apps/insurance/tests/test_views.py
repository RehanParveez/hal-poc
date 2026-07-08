from rest_framework.test import APIRequestFactory, force_authenticate
import pytest
from apps.insurance.tests.factories import InsurancePolicyFactory
from apps.insurance.views import InsurancePolicyViewSet
from apps.accounts.tests.factories import UserFactory
from apps.insurance.views import InsuranceClaimViewSet
from apps.insurance.tests.factories import InsuranceClaimFactory
from decimal import Decimal
from apps.insurance.tests.factories import InsuranceProfileFactory
 
def authed(action_map, view_cls, user, method = 'get', data=None):
  factory = APIRequestFactory()
  request = getattr(factory, method)('/', data) if data is not None else getattr(factory, method)('/')
  force_authenticate(request, user=user)
  return view_cls.as_view(action_map), request
 
@pytest.mark.django_db
class TestInsurancePolicyViewSetQuerysetScoping:
  def test_farmer_only_sees_their_own_policy(self):
    policy_a = InsurancePolicyFactory()
    policy_b = InsurancePolicyFactory()
    view, request = authed({'get': 'list'}, InsurancePolicyViewSet, policy_a.loan.farmer.user)
    response = view(request)
    returned_ids = {row['id'] for row in response.data}
    assert str(policy_a.id) in returned_ids
    assert str(policy_b.id) not in returned_ids
 
  def test_insurance_role_sees_every_policy_platform_wide(self):
    policy_a = InsurancePolicyFactory()
    policy_b = InsurancePolicyFactory()
    agent = UserFactory(role = 'insurance')
    view, request = authed({'get': 'list'}, InsurancePolicyViewSet, agent)
    response = view(request)
    returned_ids = {row['id'] for row in response.data}
    assert str(policy_a.id) in returned_ids
    assert str(policy_b.id) in returned_ids
 
  def test_shopkeeper_role_is_forbidden_from_listing(self):
    InsurancePolicyFactory()
    shopkeeper = UserFactory(role = 'shopkeeper')
    view, request = authed({'get': 'list'}, InsurancePolicyViewSet, shopkeeper)
    response = view(request)
    assert response.status_code == 403
    assert response.data['detail'].code == 'permission_denied'
 
  def test_list_response_is_a_raw_list_not_paginated(self):
    InsurancePolicyFactory()
    agent = UserFactory(role = 'insurance')
    view, request = authed({'get': 'list'}, InsurancePolicyViewSet, agent)
    response = view(request)
    assert isinstance(response.data, list)
 
  def test_status_query_param_filters_the_list(self):
    active_policy = InsurancePolicyFactory(status = 'active')
    expired_policy = InsurancePolicyFactory(status = 'expired')
    agent = UserFactory(role = 'insurance')
    view, request = authed({'get': 'list'}, InsurancePolicyViewSet, agent, data={'status': 'expired'})
    response = view(request)
    returned_ids = {row['id'] for row in response.data}
    assert str(expired_policy.id) in returned_ids
    assert str(active_policy.id) not in returned_ids
 
@pytest.mark.django_db
class TestInsurancePolicyViewSetRetrieveScoping:
  def test_a_different_farmer_gets_404_not_403(self):
    policy = InsurancePolicyFactory()
    other_farmer = UserFactory(role = 'smallholder')
    view, request = authed({'get': 'retrieve'}, InsurancePolicyViewSet, other_farmer)
    response = view(request, pk=policy.id)
    assert response.status_code == 404
 
  def test_owning_farmer_can_retrieve_their_own_policy(self):
    policy = InsurancePolicyFactory()
    view, request = authed({'get': 'retrieve'}, InsurancePolicyViewSet, policy.loan.farmer.user)
    response = view(request, pk=policy.id)
    assert response.status_code == 200
    assert response.data['id'] == str(policy.id)
 
@pytest.mark.django_db
class TestInsuranceClaimViewSetCreate:
  def test_farmer_can_file_a_claim_on_their_own_policy(self):
    policy = InsurancePolicyFactory(status = 'active')
    view, request = authed({'post': 'create'}, InsuranceClaimViewSet, policy.loan.farmer.user, method = 'post',
      data={'policy_id': str(policy.id), 'reason': 'Locust swarm destroyed the standing crop', 'claim_amount': '15000.00'})
    response = view(request)
    assert response.status_code == 201
    assert response.data['status'] == 'pending'
 
  def test_farmer_cannot_file_a_claim_on_someone_else_s_policy(self):
    policy = InsurancePolicyFactory(status = 'active')
    other_farmer = UserFactory(role = 'smallholder')
    view, request = authed({'post': 'create'}, InsuranceClaimViewSet, other_farmer, method = 'post',
      data={'policy_id': str(policy.id), 'reason': 'Trying to claim on a policy that is not mine', 'claim_amount': '15000.00'})
    response = view(request)
    assert response.status_code == 403
 
  def test_missing_policy_id_returns_400(self):
    farmer = UserFactory(role = 'smallholder')
    view, request = authed({'post': 'create'}, InsuranceClaimViewSet, farmer, method = 'post',
      data={'reason': 'No policy_id supplied at all here', 'claim_amount': '5000.00'})
    response = view(request)
    assert response.status_code == 400
 
  def test_nonexistent_policy_id_returns_404(self):
    farmer = UserFactory(role = 'smallholder')
    view, request = authed({'post': 'create'}, InsuranceClaimViewSet, farmer, method = 'post',
      data={'policy_id': '00000000-0000-0000-0000-000000000000', 'reason': 'Policy id does not exist at all', 'claim_amount': '5000.00'})
    response = view(request)
    assert response.status_code == 404
 
  def test_reason_shorter_than_minimum_length_is_rejected(self):
    policy = InsurancePolicyFactory(status = 'active')
    view, request = authed({'post': 'create'}, InsuranceClaimViewSet, policy.loan.farmer.user, method = 'post',
      data={'policy_id': str(policy.id), 'reason': 'too short', 'claim_amount': '5000.00'})
    response = view(request)
    assert response.status_code == 400
 
  def test_zero_claim_amount_is_rejected(self):
    policy = InsurancePolicyFactory(status = 'active')
    view, request = authed({'post': 'create'}, InsuranceClaimViewSet, policy.loan.farmer.user, method = 'post',
      data={'policy_id': str(policy.id), 'reason': 'A perfectly long enough reason string here', 'claim_amount': '0.00'})
    response = view(request)
    assert response.status_code == 400
 
  def test_bank_role_is_denied_at_the_permission_layer(self):
    policy = InsurancePolicyFactory(status = 'active')
    bank_user = UserFactory(role = 'bank')
    view, request = authed({'post': 'create'}, InsuranceClaimViewSet, bank_user, method = 'post',
      data={'policy_id': str(policy.id), 'reason': 'Bank role attempting to file a farmer claim', 'claim_amount': '5000.00'})
    response = view(request)
    assert response.status_code == 403
 
@pytest.mark.django_db
class TestInsuranceClaimViewSetRetrieveScoping:
  def test_a_different_farmer_gets_404_not_403(self):
    claim = InsuranceClaimFactory()
    other_farmer = UserFactory(role = 'smallholder')
    view, request = authed({'get': 'retrieve'}, InsuranceClaimViewSet, other_farmer)
    response = view(request, pk=claim.id)
    assert response.status_code == 404
 
@pytest.mark.django_db
class TestInsuranceClaimViewSetReviewAction:
  def test_insurance_role_can_review_a_pending_claim(self):
    claim = InsuranceClaimFactory(status = 'pending', claim_amount=Decimal('10000.00'))
    reviewer = UserFactory(role = 'insurance')
    view, request = authed({'patch': 'review_claim'}, InsuranceClaimViewSet, reviewer, method = 'patch',
      data={'decision': 'approved', 'approved_amount': '9000.00'})
    response = view(request, pk=claim.id)
    assert response.status_code == 200
    assert response.data['status'] == 'approved'
 
  def test_farmer_role_is_denied_review_access(self):
    claim = InsuranceClaimFactory(status = 'pending')
    view, request = authed({'patch': 'review_claim'}, InsuranceClaimViewSet, claim.claimed_by, method = 'patch',
      data={'decision': 'approved', 'approved_amount': '1000.00'})
    response = view(request, pk=claim.id)
    assert response.status_code == 403
 
  def test_reviewing_an_already_resolved_claim_returns_400(self):
    claim = InsuranceClaimFactory(status = 'approved')
    reviewer = UserFactory(role = 'insurance')
    view, request = authed({'patch': 'review_claim'}, InsuranceClaimViewSet, reviewer, method = 'patch',
      data={'decision': 'rejected'})
    response = view(request, pk=claim.id)
    assert response.status_code == 400
 
  def test_an_insurance_agent_from_an_unrelated_insurer_can_still_review_the_claim(self):
    actual_insurer = InsuranceProfileFactory(company_name = 'EFU Life')
    policy = InsurancePolicyFactory(insurer=actual_insurer)
    claim = InsuranceClaimFactory(policy=policy, status = 'pending')
    unrelated_agent = UserFactory(role = 'insurance')
    view, request = authed({'patch': 'review_claim'}, InsuranceClaimViewSet, unrelated_agent, method = 'patch',
      data={'decision': 'approved', 'approved_amount': '1000.00'})
    response = view(request, pk=claim.id)
    assert response.status_code == 200
 
  def test_missing_approved_amount_on_approval_returns_400(self):
    claim = InsuranceClaimFactory(status = 'pending')
    reviewer = UserFactory(role = 'insurance')
    view, request = authed({'patch': 'review_claim'}, InsuranceClaimViewSet, reviewer, method = 'patch',
      data={'decision': 'approved'})
    response = view(request, pk=claim.id)
    assert response.status_code == 400