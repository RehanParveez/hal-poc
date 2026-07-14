import pytest
from apps.accounts.tests.factories import FarmerProfileFactory, BankProfileFactory, UserFactory
from apps.crops.tests.factories import CropTypeFactory, CropLifecycleMilestoneFactory
from apps.loans.services import LoanApplicationService
from decimal import Decimal
from apps.loans.tests.factories import LoanApplicationFactory
import threading
from queue import Queue
from django.db import connections
from apps.escrow.models import EscrowWallet
from shared.exceptions import LoanAlreadyDisbursedError
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.loans.views import LoanApplicationViewSet
from apps.land.tests.factories import TenantAgreementFactory
from unittest.mock import patch

@pytest.mark.django_db
class TestApplyForLoan:
  def test_creates_loan_with_submitted_status(self):
    farmer = FarmerProfileFactory()
    bank = BankProfileFactory()
    crop = CropTypeFactory()
    loan = LoanApplicationService.apply_for_loan(farmer_profile=farmer, bank_profile=bank,
      validated_data={'crop': crop, 'acres_applied_for': Decimal('3.00'), 'requested_amount': Decimal('50000.00')})
    assert loan.status == 'submitted'
    assert loan.approved_amount is None
 
@pytest.mark.django_db
class TestApproveLoan:
  def test_approving_a_submitted_loan_sets_bank_approved_status_and_amount(self):
    loan = LoanApplicationFactory(status = 'submitted')
    approved = LoanApplicationService.approve_loan(loan_id=loan.id, bank_profile=loan.bank,
      approved_amount=Decimal('80000.00'), interest_rate_pct=Decimal('12.50'))
    assert approved.status == 'bank_approved'
    assert approved.approved_amount == Decimal('80000.00')
    assert approved.approved_at is not None
 
  def test_rejects_approval_from_a_bank_that_does_not_own_the_loan(self):
    loan = LoanApplicationFactory(status = 'submitted')
    other_bank = BankProfileFactory()
    with pytest.raises(PermissionError):
      LoanApplicationService.approve_loan(loan_id=loan.id, bank_profile=other_bank,
        approved_amount=Decimal('80000.00'), interest_rate_pct=Decimal('12.50'))
 
  def test_cannot_approve_a_loan_that_is_already_approved(self):
    loan = LoanApplicationFactory(status = 'bank_approved')
    with pytest.raises(ValueError):
      LoanApplicationService.approve_loan(loan_id=loan.id, bank_profile=loan.bank,
        approved_amount=Decimal('80000.00'), interest_rate_pct=Decimal('12.50'))
 
  def test_zero_approved_amount_is_rejected(self):
    loan = LoanApplicationFactory(status = 'submitted')
    with pytest.raises(ValueError):
      LoanApplicationService.approve_loan(loan_id=loan.id, bank_profile=loan.bank,
        approved_amount=Decimal('0.00'), interest_rate_pct=Decimal('12.50'))
 
  def test_negative_approved_amount_is_rejected(self):
    loan = LoanApplicationFactory(status = 'submitted')
    with pytest.raises(ValueError):
      LoanApplicationService.approve_loan(loan_id=loan.id, bank_profile=loan.bank,
        approved_amount=Decimal('-500.00'), interest_rate_pct=Decimal('12.50'))
 
@pytest.mark.django_db
class TestRejectLoan:
  def test_rejecting_a_submitted_loan_sets_status_and_reason(self):
    loan = LoanApplicationFactory(status = 'submitted')
    rejected = LoanApplicationService.reject_loan(loan_id=loan.id, bank_profile=loan.bank,
      rejection_reason = 'not enough collateral')
    assert rejected.status == 'rejected'
    assert rejected.rejection_reason == 'not enough collateral'
 
  def test_can_reject_a_previously_approved_loan_before_disbursement(self):
    loan = LoanApplicationFactory(status = 'bank_approved')
    rejected = LoanApplicationService.reject_loan(loan_id=loan.id, bank_profile=loan.bank, rejection_reason = 'Changed mind')
    assert rejected.status == 'rejected'
 
  def test_cannot_reject_an_already_disbursed_loan(self):
    loan = LoanApplicationFactory(status = 'disbursed')
    with pytest.raises(ValueError):
      LoanApplicationService.reject_loan(loan_id=loan.id, bank_profile=loan.bank, rejection_reason = 'too late')
 
  def test_rejects_from_a_bank_that_does_not_own_the_loan(self):
    loan = LoanApplicationFactory(status = 'submitted')
    other_bank = BankProfileFactory()
    with pytest.raises(PermissionError):
      LoanApplicationService.reject_loan(loan_id=loan.id, bank_profile=other_bank, rejection_reason = 'not yours')
 
@pytest.mark.django_db
class TestDisburseLoan:
  def _approved_loan_with_milestone(self):
    loan = LoanApplicationFactory(status = 'submitted', requested_amount=Decimal('100000.00'))
    CropLifecycleMilestoneFactory(crop=loan.crop, phase_number=1, unlock_pct=Decimal('30.00'), allowed_input_categories=['seed'])
    return LoanApplicationService.approve_loan(loan_id=loan.id, bank_profile=loan.bank,
      approved_amount=Decimal('100000.00'), interest_rate_pct=Decimal('10.00'))
 
  def test_disbursing_an_approved_loan_creates_its_escrow(self):
    loan = self._approved_loan_with_milestone()
    disbursed, escrow = LoanApplicationService.disburse_loan(loan_id=loan.id, bank_profile=loan.bank)
    assert disbursed.status == 'disbursed'
    assert escrow.loan == disbursed
    assert escrow.total_funded == Decimal('100000.00')
 
  def test_disbursing_twice_raises_loan_already_disbursed(self):
    loan = self._approved_loan_with_milestone()
    LoanApplicationService.disburse_loan(loan_id=loan.id, bank_profile=loan.bank)
    with pytest.raises(LoanAlreadyDisbursedError):
      LoanApplicationService.disburse_loan(loan_id=loan.id, bank_profile=loan.bank)
 
  def test_cannot_disburse_a_loan_that_is_not_yet_approved(self):
    loan = LoanApplicationFactory(status = 'submitted')
    with pytest.raises(ValueError):
      LoanApplicationService.disburse_loan(loan_id=loan.id, bank_profile=loan.bank)
 
  def test_disbursement_from_a_bank_that_does_not_own_the_loan_is_rejected(self):
    loan = self._approved_loan_with_milestone()
    other_bank = BankProfileFactory()
    with pytest.raises(PermissionError):
      LoanApplicationService.disburse_loan(loan_id=loan.id, bank_profile=other_bank)
 
  def test_failed_escrow_creation_rolls_back_the_disbursement_entirely(self):
    loan = LoanApplicationFactory(status = 'submitted', requested_amount=Decimal('50000.00'))
    approved = LoanApplicationService.approve_loan(loan_id=loan.id, bank_profile=loan.bank,
      approved_amount=Decimal('50000.00'), interest_rate_pct=Decimal('10.00'))
    with pytest.raises(ValueError):
      LoanApplicationService.disburse_loan(loan_id=approved.id, bank_profile=approved.bank)
    approved.refresh_from_db()
    assert approved.status == 'bank_approved', "loan stuck 'disbursed' with no escrow -- rollback isn't atomic across both steps"
    assert not EscrowWallet.objects.filter(loan=approved).exists()
 
  def test_retry_after_a_failed_disbursement_succeeds_once_the_milestone_is_fixed(self):
    loan = LoanApplicationFactory(status = 'submitted', requested_amount=Decimal('50000.00'))
    approved = LoanApplicationService.approve_loan(loan_id=loan.id, bank_profile=loan.bank,
      approved_amount=Decimal('50000.00'), interest_rate_pct=Decimal('10.00'))
    with pytest.raises(ValueError):
      LoanApplicationService.disburse_loan(loan_id=approved.id, bank_profile=approved.bank)
    CropLifecycleMilestoneFactory(crop=approved.crop, phase_number=1, unlock_pct=Decimal('30.00'), allowed_input_categories=['seed'])
    disbursed, escrow = LoanApplicationService.disburse_loan(loan_id=approved.id, bank_profile=approved.bank)
    assert disbursed.status == 'disbursed'
    assert escrow is not None
 
@pytest.mark.django_db(transaction=True)
class TestDisburseLoanConcurrency:
  @patch('apps.notifications.services.NotificationService.notify')
  def test_concurrent_disbursement_attempts_only_one_succeeds(self, mock_notify):
    loan = LoanApplicationFactory(status = 'submitted', requested_amount=Decimal('100000.00'))
    CropLifecycleMilestoneFactory(crop=loan.crop, phase_number=1, unlock_pct=Decimal('30.00'), allowed_input_categories=['seed'])
    approved = LoanApplicationService.approve_loan(loan_id=loan.id, bank_profile=loan.bank,
      approved_amount=Decimal('100000.00'), interest_rate_pct=Decimal('10.00'))
    barrier = threading.Barrier(2)
    results = Queue()
    def worker():
      barrier.wait()
      try:
        LoanApplicationService.disburse_loan(loan_id=approved.id, bank_profile=approved.bank)
        results.put('success')
      except LoanAlreadyDisbursedError:
        results.put('failure')
      finally:
        connections.close_all()
    threads = [threading.Thread(target=worker) for _ in range(2)]
    for t in threads: t.start()
    for t in threads: t.join()
    outcomes = list(results.queue)
    assert outcomes.count('success') == 1, f"expected exactly one to succeed, got: {outcomes}"
    assert EscrowWallet.objects.filter(loan=approved).count() == 1

@pytest.mark.django_db
class TestLoanApplicationCreateValidation:
  def test_smallholder_can_apply_within_owned_acres(self):
    user = UserFactory(role='smallholder')
    user.farmer_profile.total_owned_acres = Decimal('10.00')
    user.farmer_profile.save()
    bank, crop = BankProfileFactory(), CropTypeFactory()
    req = APIRequestFactory().post('/loans/applications/', {'bank': bank.id, 'crop': crop.id,
      'acres_applied_for': '5.00', 'requested_amount': '50000.00'})
    force_authenticate(req, user=user)
    assert LoanApplicationViewSet.as_view({'post': 'create'})(req).status_code == 201
 
  def test_smallholder_applying_beyond_owned_acres_is_rejected(self):
    user = UserFactory(role = 'smallholder')
    user.farmer_profile.total_owned_acres = Decimal('3.00')
    user.farmer_profile.save()
    bank, crop = BankProfileFactory(), CropTypeFactory()
    req = APIRequestFactory().post('/loans/applications/', {'bank': bank.id, 'crop': crop.id,
      'acres_applied_for': '5.00', 'requested_amount': '50000.00'})
    force_authenticate(req, user=user)
    assert LoanApplicationViewSet.as_view({'post': 'create'})(req).status_code == 400
 
  def test_smallholder_providing_a_tenant_agreement_is_rejected(self, request):
    user = UserFactory(role='smallholder')
    bank, crop = BankProfileFactory(), CropTypeFactory()
    agreement = TenantAgreementFactory(tenant=user.farmer_profile)
    request.addfinalizer(agreement.delete)
    req = APIRequestFactory().post('/loans/applications/', {'bank': bank.id, 'crop': crop.id,
      'tenant_agreement': agreement.id, 'acres_applied_for': '2.00', 'requested_amount': '20000.00'})
    force_authenticate(req, user=user)
    assert LoanApplicationViewSet.as_view({'post': 'create'})(req).status_code == 400
 
  def test_tenant_without_a_tenant_agreement_is_rejected(self):
    user = UserFactory(role='tenant')
    bank, crop = BankProfileFactory(), CropTypeFactory()
    req = APIRequestFactory().post('/loans/applications/', {'bank': bank.id, 'crop': crop.id,
      'acres_applied_for': '2.00', 'requested_amount': '20000.00'})
    force_authenticate(req, user=user)
    assert LoanApplicationViewSet.as_view({'post': 'create'})(req).status_code == 400
 
  def test_tenant_with_an_unapproved_agreement_is_rejected(self, request):
    user = UserFactory(role = 'tenant')
    bank, crop = BankProfileFactory(), CropTypeFactory()
    agreement = TenantAgreementFactory(tenant=user.farmer_profile, landowner_approved=False, status = 'pending')
    request.addfinalizer(agreement.delete)
    req = APIRequestFactory().post('/loans/applications/', {'bank': bank.id, 'crop': crop.id,
      'tenant_agreement': agreement.id, 'acres_applied_for': '2.00', 'requested_amount': '20000.00'})
    force_authenticate(req, user=user)
    assert LoanApplicationViewSet.as_view({'post': 'create'})(req).status_code == 400
 
  def test_tenant_using_someone_else_s_agreement_is_rejected(self):
    user = UserFactory(role = 'tenant')
    other_agreement = TenantAgreementFactory(landowner_approved=True, status = 'active')
    bank, crop = BankProfileFactory(), CropTypeFactory()
    req = APIRequestFactory().post('/loans/applications/', {'bank': bank.id, 'crop': crop.id,
      'tenant_agreement': other_agreement.id, 'acres_applied_for': '2.00', 'requested_amount': '20000.00'})
    force_authenticate(req, user=user)
    assert LoanApplicationViewSet.as_view({'post': 'create'})(req).status_code == 400
 
  def test_tenant_applying_beyond_leased_acres_is_rejected(self, request):
    user = UserFactory(role='tenant')
    agreement = TenantAgreementFactory(tenant=user.farmer_profile, leased_acres=Decimal('4.00'),
      landowner_approved=True, status='active')
    request.addfinalizer(agreement.delete)
    bank, crop = BankProfileFactory(), CropTypeFactory()
    req = APIRequestFactory().post('/loans/applications/', {'bank': bank.id, 'crop': crop.id,
      'tenant_agreement': agreement.id, 'acres_applied_for': '6.00', 'requested_amount': '20000.00'})
    force_authenticate(req, user=user)
    assert LoanApplicationViewSet.as_view({'post': 'create'})(req).status_code == 400
 
  def test_non_farmer_role_cannot_apply_for_a_loan(self):
    user = UserFactory(role='shopkeeper')
    bank, crop = BankProfileFactory(), CropTypeFactory()
    req = APIRequestFactory().post('/loans/applications/', {'bank': bank.id, 'crop': crop.id,
      'acres_applied_for': '2.00', 'requested_amount': '20000.00'})
    force_authenticate(req, user=user)
    assert LoanApplicationViewSet.as_view({'post': 'create'})(req).status_code == 403
 
  @pytest.fixture
  def loan_data(db):
    viewer = UserFactory(role='smallholder')
    my_loan = LoanApplicationFactory(farmer=viewer.farmer_profile)
    return {"user": viewer, "loan": my_loan}

  def test_bank_sees_only_loans_assigned_to_their_own_bank(self):
    bank_user, other_bank_user = UserFactory(role = 'bank'), UserFactory(role = 'bank')
    my_loan = LoanApplicationFactory(bank=bank_user.bank_profile)
    LoanApplicationFactory(bank=other_bank_user.bank_profile)
    req = APIRequestFactory().get('/loans/applications/')
    force_authenticate(req, user=bank_user)
    response = LoanApplicationViewSet.as_view({'get': 'list'})(req)
    assert {row['id'] for row in response.data['results']} == {str(my_loan.id)}
 
  def test_unrelated_role_sees_nothing(self):
    LoanApplicationFactory()
    shopkeeper = UserFactory(role = 'shopkeeper')
    req = APIRequestFactory().get('/loans/applications/')
    force_authenticate(req, user=shopkeeper)
    response = LoanApplicationViewSet.as_view({'get': 'list'})(req)
    assert response.data['results'] == []
 
@pytest.mark.django_db
class TestLoanActionOwnership:
  def test_approve_action_blocks_a_different_bank(self):
    loan = LoanApplicationFactory(status = 'submitted')
    other_bank_user = UserFactory(role = 'bank')
    req = APIRequestFactory().patch(f'/loans/applications/{loan.id}/approve/',
      {'approved_amount': '50000.00', 'interest_rate_pct': '10.00'})
    force_authenticate(req, user=other_bank_user)
    response = LoanApplicationViewSet.as_view({'patch': 'approve'})(req, pk=str(loan.id))
    assert response.status_code == 403
 
  def test_disburse_by_a_non_bank_role_is_blocked_at_the_permission_layer(self):
    loan = LoanApplicationFactory(status = 'bank_approved')
    farmer = UserFactory(role = 'smallholder')
    req = APIRequestFactory().post(f'/loans/applications/{loan.id}/disburse/')
    force_authenticate(req, user=farmer)
    response = LoanApplicationViewSet.as_view({'post': 'disburse'})(req, pk=str(loan.id))
    assert response.status_code == 403