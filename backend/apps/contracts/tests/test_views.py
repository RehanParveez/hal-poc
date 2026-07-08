from apps.accounts.tests.factories import FarmerProfileFactory
from apps.loans.tests.factories import LoanApplicationFactory
import pytest
from apps.accounts.tests.factories import UserFactory
from rest_framework.test import APIRequestFactory
from apps.crops.tests.factories import CropTypeFactory
from rest_framework.test import force_authenticate
from apps.contracts.views import CropContractViewSet
from apps.accounts.tests.factories import FactoryProfileFactory
import uuid
from decimal import Decimal
from apps.contracts.tests.factories import CropContractFactory
from apps.contracts.services import FarmerContractAllocationService
from apps.contracts.views import FarmerContractAllocationViewSet

def make_disbursed_loan(crop, farmer=None):
  farmer = farmer or FarmerProfileFactory()
  return LoanApplicationFactory(farmer=farmer, crop=crop, status = 'disbursed')

@pytest.mark.django_db
class TestCropContractCreatePermissionsAndValidation:
  def _payload(self, crop, **overrides):
    base = {'crop': str(crop.id), 'required_kg': '5000.00', 'base_price_per_kg': '40.00',
      'payment_defer_days': 15, 'delivery_deadline': '2027-01-01'}
    base.update(overrides)
    return base

  def test_factory_role_can_create_a_contract(self):
    factory_user = UserFactory(role = 'factory')
    req = APIRequestFactory().post('/contracts/cropcontracts/', self._payload(CropTypeFactory()))
    force_authenticate(req, user=factory_user)
    response = CropContractViewSet.as_view({'post': 'create'})(req)
    assert response.status_code == 201
    assert response.data['status'] == 'open'

  def test_non_factory_role_cannot_create(self):
    farmer_user = UserFactory(role = 'smallholder')
    req = APIRequestFactory().post('/contracts/cropcontracts/', self._payload(CropTypeFactory()))
    force_authenticate(req, user=farmer_user)
    assert CropContractViewSet.as_view({'post': 'create'})(req).status_code == 403

  def test_unauthenticated_cannot_create(self):
    req = APIRequestFactory().post('/contracts/cropcontracts/', self._payload(CropTypeFactory()))
    assert CropContractViewSet.as_view({'post': 'create'})(req).status_code == 401

  def test_zero_required_kg_is_rejected(self):
    factory_user = UserFactory(role = 'factory')
    req = APIRequestFactory().post('/contracts/cropcontracts/', self._payload(CropTypeFactory(), required_kg='0.00'))
    force_authenticate(req, user=factory_user)
    assert CropContractViewSet.as_view({'post': 'create'})(req).status_code == 400

  def test_zero_base_price_per_kg_is_rejected(self):
    factory_user = UserFactory(role = 'factory')
    req = APIRequestFactory().post('/contracts/cropcontracts/', self._payload(CropTypeFactory(), base_price_per_kg='0.00'))
    force_authenticate(req, user=factory_user)
    assert CropContractViewSet.as_view({'post': 'create'})(req).status_code == 400

  @pytest.mark.parametrize("bad_days", [0, 31])
  def test_payment_defer_days_outside_1_to_30_is_rejected(self, bad_days):
    factory_user = UserFactory(role = 'factory')
    req = APIRequestFactory().post('/contracts/cropcontracts/', self._payload(CropTypeFactory(), payment_defer_days=bad_days))
    force_authenticate(req, user=factory_user)
    assert CropContractViewSet.as_view({'post': 'create'})(req).status_code == 400

  @pytest.mark.parametrize("boundary_days", [1, 30])
  def test_payment_defer_days_boundary_values_are_accepted(self, boundary_days):
    factory_user = UserFactory(role = 'factory')
    req = APIRequestFactory().post('/contracts/cropcontracts/', self._payload(CropTypeFactory(), payment_defer_days=boundary_days))
    force_authenticate(req, user=factory_user)
    assert CropContractViewSet.as_view({'post': 'create'})(req).status_code == 201

  def test_delivery_deadline_in_the_past_is_now_rejected(self):
    factory_user = UserFactory(role = 'factory')
    req = APIRequestFactory().post('/contracts/cropcontracts/', self._payload(CropTypeFactory(), delivery_deadline = '2025-01-01'))
    force_authenticate(req, user=factory_user)
    response = CropContractViewSet.as_view({'post': 'create'})(req)
    assert response.status_code == 400

  def test_factory_field_cannot_be_spoofed_by_the_client(self):
    factory_user = UserFactory(role = 'factory')
    other_factory = FactoryProfileFactory()  
    req = APIRequestFactory().post('/contracts/cropcontracts/', self._payload(CropTypeFactory(), factory=str(other_factory.id)))
    force_authenticate(req, user=factory_user)
    response = CropContractViewSet.as_view({'post': 'create'})(req)
    assert str(response.data['factory']) == str(factory_user.factory_profile.id)

@pytest.mark.django_db
class TestCropContractListVisibility:
  def test_any_authenticated_role_can_list_all_contracts(self):
    contract = CropContractFactory()
    req = APIRequestFactory().get('/contracts/cropcontracts/')
    force_authenticate(req, user=UserFactory(role = 'smallholder'))
    response = CropContractViewSet.as_view({'get': 'list'})(req)
    assert str(contract.id) in {row['id'] for row in response.data['results']}

  def test_unauthenticated_cannot_list(self):
    req = APIRequestFactory().get('/contracts/cropcontracts/')
    assert CropContractViewSet.as_view({'get': 'list'})(req).status_code == 401

  def test_filter_by_crop_code_is_case_insensitive(self):
    contract = CropContractFactory(crop=CropTypeFactory(code = 'CONTRACTTEST'))
    other_contract = CropContractFactory()
    req = APIRequestFactory().get('/contracts/cropcontracts/', {'crop': 'contracttest'})
    force_authenticate(req, user=UserFactory(role = 'smallholder'))
    response = CropContractViewSet.as_view({'get': 'list'})(req)
    ids = {row['id'] for row in response.data['results']}
    assert str(contract.id) in ids and str(other_contract.id) not in ids

  def test_filter_by_status(self):
    open_contract = CropContractFactory(status = 'open')
    allocated_contract = CropContractFactory(status = 'allocated')
    req = APIRequestFactory().get('/contracts/cropcontracts/', {'status': 'allocated'})
    force_authenticate(req, user=UserFactory(role = 'smallholder'))
    response = CropContractViewSet.as_view({'get': 'list'})(req)
    ids = {row['id'] for row in response.data['results']}
    assert str(allocated_contract.id) in ids and str(open_contract.id) not in ids
    
@pytest.mark.django_db
class TestAllocateActionEndpoint:
  def test_non_farmer_role_is_blocked(self):
    contract = CropContractFactory()
    loan = make_disbursed_loan(contract.crop)
    req = APIRequestFactory().post(f'/contracts/cropcontracts/{contract.id}/allocate/',
      {'loan_id': str(loan.id), 'committed_kg': '10.00'})
    user = UserFactory(role = 'factory')
    force_authenticate(req, user=user)
    assert CropContractViewSet.as_view({'post': 'allocate'})(req, pk=str(contract.id)).status_code == 403

  def test_missing_loan_id_returns_400(self):
    contract = CropContractFactory()
    req = APIRequestFactory().post(f'/contracts/cropcontracts/{contract.id}/allocate/', {'committed_kg': '10.00'})
    force_authenticate(req, user=UserFactory(role = 'smallholder'))
    assert CropContractViewSet.as_view({'post': 'allocate'})(req, pk=str(contract.id)).status_code == 400

  def test_missing_committed_kg_returns_400(self):
    contract = CropContractFactory()
    loan = make_disbursed_loan(contract.crop)
    req = APIRequestFactory().post(f'/contracts/cropcontracts/{contract.id}/allocate/', {'loan_id': str(loan.id)})
    force_authenticate(req, user=loan.farmer.user)
    assert CropContractViewSet.as_view({'post': 'allocate'})(req, pk=str(contract.id)).status_code == 400

  def test_nonexistent_loan_id_returns_404(self):
    contract = CropContractFactory()
    req = APIRequestFactory().post(f'/contracts/cropcontracts/{contract.id}/allocate/',
      {'loan_id': str(uuid.uuid4()), 'committed_kg': '10.00'})
    force_authenticate(req, user=UserFactory(role = 'smallholder'))
    assert CropContractViewSet.as_view({'post': 'allocate'})(req, pk=str(contract.id)).status_code == 404

  def test_nonexistent_contract_returns_404(self):
    loan = LoanApplicationFactory(status = 'disbursed')
    fake_id = str(uuid.uuid4())
    req = APIRequestFactory().post(f'/contracts/cropcontracts/{fake_id}/allocate/',
      {'loan_id': str(loan.id), 'committed_kg': '10.00'})
    force_authenticate(req, user=loan.farmer.user)
    assert CropContractViewSet.as_view({'post': 'allocate'})(req, pk=fake_id).status_code == 404

  def test_successful_allocation_returns_201(self):
    contract = CropContractFactory(required_kg=Decimal('1000.00'))
    loan = make_disbursed_loan(contract.crop)
    req = APIRequestFactory().post(f'/contracts/cropcontracts/{contract.id}/allocate/',
      {'loan_id': str(loan.id), 'committed_kg': '200.00'})
    force_authenticate(req, user=loan.farmer.user)
    assert CropContractViewSet.as_view({'post': 'allocate'})(req, pk=str(contract.id)).status_code == 201

  def test_allocating_with_someone_else_s_loan_returns_403(self):
    contract = CropContractFactory()
    loan = make_disbursed_loan(contract.crop)
    req = APIRequestFactory().post(f'/contracts/cropcontracts/{contract.id}/allocate/',
      {'loan_id': str(loan.id), 'committed_kg': '10.00'})
    force_authenticate(req, user=UserFactory(role = 'smallholder'))
    assert CropContractViewSet.as_view({'post': 'allocate'})(req, pk=str(contract.id)).status_code == 403

  def test_over_capacity_allocation_returns_409_via_the_global_exception_handler(self):
    contract = CropContractFactory(required_kg=Decimal('100.00'), allocated_kg=Decimal('80.00'))
    loan = make_disbursed_loan(contract.crop)
    req = APIRequestFactory().post(f'/contracts/cropcontracts/{contract.id}/allocate/',
      {'loan_id': str(loan.id), 'committed_kg': '21.00'})
    force_authenticate(req, user=loan.farmer.user)
    response = CropContractViewSet.as_view({'post': 'allocate'})(req, pk=str(contract.id))
    assert response.status_code == 409
    assert response.data['error'] == 'CONTRACT_FULLY_ALLOCATED'

  def test_committed_kg_as_form_string_zero_is_now_rejected(self):
    contract = CropContractFactory(required_kg=Decimal('100.00'))
    loan = make_disbursed_loan(contract.crop)
    req = APIRequestFactory().post(f'/contracts/cropcontracts/{contract.id}/allocate/',
      {'loan_id': str(loan.id), 'committed_kg': '0'})
    force_authenticate(req, user=loan.farmer.user)
    response = CropContractViewSet.as_view({'post': 'allocate'})(req, pk=str(contract.id))
    assert response.status_code == 400

  def test_committed_kg_as_json_number_zero_is_blocked(self):
    contract = CropContractFactory(required_kg=Decimal('100.00'))
    loan = make_disbursed_loan(contract.crop)
    req = APIRequestFactory().post(f'/contracts/cropcontracts/{contract.id}/allocate/',
      {'loan_id': str(loan.id), 'committed_kg': 0}, format = 'json')
    force_authenticate(req, user=loan.farmer.user)
    response = CropContractViewSet.as_view({'post': 'allocate'})(req, pk=str(contract.id))
    assert response.status_code == 400

  def test_negative_committed_kg_is_rejected_through_the_view(self):
    contract = CropContractFactory(required_kg=Decimal('100.00'), allocated_kg=Decimal('50.00'))
    loan = make_disbursed_loan(contract.crop)
    req = APIRequestFactory().post(f'/contracts/cropcontracts/{contract.id}/allocate/',
      {'loan_id': str(loan.id), 'committed_kg': '-30.00'})
    force_authenticate(req, user=loan.farmer.user)
    response = CropContractViewSet.as_view({'post': 'allocate'})(req, pk=str(contract.id))
    assert response.status_code == 400
    contract.refresh_from_db()
    assert contract.allocated_kg == Decimal('50.00')
    
@pytest.mark.django_db
class TestFarmerContractAllocationViewSetScoping:
  def test_farmer_sees_only_their_own_allocations(self):
    contract = CropContractFactory(required_kg=Decimal('1000.00'))
    loan_a, loan_b = make_disbursed_loan(contract.crop), make_disbursed_loan(contract.crop)
    allocation_a = FarmerContractAllocationService.allocate_farmer(contract.id, loan_a.farmer, loan_a, Decimal('100.00'))
    FarmerContractAllocationService.allocate_farmer(contract.id, loan_b.farmer, loan_b, Decimal('100.00'))
    req = APIRequestFactory().get('/contracts/allocations/')
    force_authenticate(req, user=loan_a.farmer.user)
    response = FarmerContractAllocationViewSet.as_view({'get': 'list'})(req)
    assert {row['id'] for row in response.data['results']} == {str(allocation_a.id)}

  def test_factory_sees_only_allocations_under_their_own_contracts(self):
    contract = CropContractFactory(required_kg=Decimal('1000.00'))
    other_contract = CropContractFactory(required_kg=Decimal('1000.00'))
    loan_a = make_disbursed_loan(contract.crop)
    loan_b = make_disbursed_loan(other_contract.crop)
    allocation_a = FarmerContractAllocationService.allocate_farmer(contract.id, loan_a.farmer, loan_a, Decimal('100.00'))
    FarmerContractAllocationService.allocate_farmer(other_contract.id, loan_b.farmer, loan_b, Decimal('100.00'))
    req = APIRequestFactory().get('/contracts/allocations/')
    force_authenticate(req, user=contract.factory.user)
    response = FarmerContractAllocationViewSet.as_view({'get': 'list'})(req)
    assert {row['id'] for row in response.data['results']} == {str(allocation_a.id)}

  def test_unrelated_role_sees_an_empty_list(self):
    contract = CropContractFactory(required_kg=Decimal('1000.00'))
    loan = make_disbursed_loan(contract.crop)
    FarmerContractAllocationService.allocate_farmer(contract.id, loan.farmer, loan, Decimal('100.00'))
    req = APIRequestFactory().get('/contracts/allocations/')
    force_authenticate(req, user=UserFactory(role = 'bank'))
    response = FarmerContractAllocationViewSet.as_view({'get': 'list'})(req)
    assert response.data['results'] == []

  def test_unauthenticated_gets_401(self):
    req = APIRequestFactory().get('/contracts/allocations/')
    assert FarmerContractAllocationViewSet.as_view({'get': 'list'})(req).status_code == 401