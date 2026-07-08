from apps.accounts.tests.factories import FarmerProfileFactory
from apps.loans.tests.factories import LoanApplicationFactory
import pytest
from apps.contracts.services import CropContractService
from apps.accounts.tests.factories import FactoryProfileFactory
from apps.crops.tests.factories import CropTypeFactory
from decimal import Decimal
from datetime import date
from apps.contracts.tests.factories import CropContractFactory
from apps.contracts.services import FarmerContractAllocationService
from shared.exceptions import ContractFullyAllocatedError
import threading
from queue import Queue
from django.db import connections
from apps.contracts.models import FarmerContractAllocation
 
def make_disbursed_loan(crop, farmer = None):
  farmer = farmer or FarmerProfileFactory()
  return LoanApplicationFactory(farmer=farmer, crop=crop, status = 'disbursed')
 
@pytest.mark.django_db
class TestCreateContract:
  def test_creates_contract_with_open_status_and_zero_allocated_by_default(self):
    contract = CropContractService.create_contract(FactoryProfileFactory(), {
      'crop': CropTypeFactory(), 'required_kg': Decimal('5000.00'),
      'base_price_per_kg': Decimal('40.00'), 'delivery_deadline': date.today(),
    })
    assert contract.status == 'open'
    assert contract.allocated_kg == Decimal('0')
 
@pytest.mark.django_db
class TestCloseContractIfFull:
  def test_flips_to_allocated_when_allocated_kg_meets_required_kg(self):
    contract = CropContractFactory(required_kg=Decimal('100.00'), allocated_kg=Decimal('100.00'))
    CropContractService.close_contract_if_full(contract)
    contract.refresh_from_db()
    assert contract.status == 'allocated'
 
  def test_leaves_status_untouched_while_still_short(self):
    contract = CropContractFactory(required_kg=Decimal('100.00'), allocated_kg=Decimal('60.00'))
    CropContractService.close_contract_if_full(contract)
    contract.refresh_from_db()
    assert contract.status == 'open'
 
@pytest.mark.django_db
class TestAllocateFarmerGuardRails:
  def test_successful_allocation_updates_contract_and_creates_row(self):
    contract = CropContractFactory(required_kg=Decimal('1000.00'), allocated_kg=Decimal('0'))
    loan = make_disbursed_loan(contract.crop)
    allocation = FarmerContractAllocationService.allocate_farmer(contract.id, loan.farmer, loan, Decimal('300.00'))
    contract.refresh_from_db()
    assert allocation.committed_kg == Decimal('300.00')
    assert contract.allocated_kg == Decimal('300.00')
    assert contract.status == 'open'
 
  def test_rejects_allocation_to_a_contract_that_is_not_open(self):
    contract = CropContractFactory(status = 'allocated')
    loan = make_disbursed_loan(contract.crop)
    with pytest.raises(ValueError):
      FarmerContractAllocationService.allocate_farmer(contract.id, loan.farmer, loan, Decimal('10.00'))
 
  def test_rejects_when_loan_does_not_belong_to_the_farmer(self):
    contract = CropContractFactory()
    loan = make_disbursed_loan(contract.crop)
    with pytest.raises(PermissionError):
      FarmerContractAllocationService.allocate_farmer(contract.id, FarmerProfileFactory(), loan, Decimal('10.00'))
 
  def test_rejects_when_loan_is_not_yet_disbursed(self):
    contract = CropContractFactory()
    farmer = FarmerProfileFactory()
    loan = LoanApplicationFactory(farmer=farmer, crop=contract.crop, status = 'bank_approved')
    with pytest.raises(ValueError):
      FarmerContractAllocationService.allocate_farmer(contract.id, farmer, loan, Decimal('10.00'))
 
  def test_rejects_when_loan_crop_does_not_match_contract_crop(self):
    contract = CropContractFactory()
    farmer = FarmerProfileFactory()
    loan = LoanApplicationFactory(farmer=farmer, crop=CropTypeFactory(), status = 'disbursed')
    with pytest.raises(ValueError):
      FarmerContractAllocationService.allocate_farmer(contract.id, farmer, loan, Decimal('10.00'))
 
  def test_rejects_a_second_allocation_by_the_same_farmer_to_the_same_contract(self):
    contract = CropContractFactory(required_kg=Decimal('1000.00'))
    loan = make_disbursed_loan(contract.crop)
    FarmerContractAllocationService.allocate_farmer(contract.id, loan.farmer, loan, Decimal('100.00'))
    loan2 = make_disbursed_loan(contract.crop, farmer=loan.farmer)
    with pytest.raises(ValueError, match = "already allocated"):
      FarmerContractAllocationService.allocate_farmer(contract.id, loan.farmer, loan2, Decimal('50.00'))
 
  def test_rejects_committed_kg_beyond_remaining_capacity(self):
    contract = CropContractFactory(required_kg=Decimal('100.00'), allocated_kg=Decimal('60.00'))
    loan = make_disbursed_loan(contract.crop)
    with pytest.raises(ContractFullyAllocatedError) as exc_info:
      FarmerContractAllocationService.allocate_farmer(contract.id, loan.farmer, loan, Decimal('41.00'))
    assert exc_info.value.available == Decimal('40.00')
 
  def test_allows_committed_kg_exactly_equal_to_remaining_capacity_and_closes_the_contract(self):
    contract = CropContractFactory(required_kg=Decimal('100.00'), allocated_kg=Decimal('60.00'))
    loan = make_disbursed_loan(contract.crop)
    FarmerContractAllocationService.allocate_farmer(contract.id, loan.farmer, loan, Decimal('40.00'))
    contract.refresh_from_db()
    assert contract.allocated_kg == Decimal('100.00')
    assert contract.status == 'allocated'
 
  def test_negative_committed_kg_is_rejected(self):
    contract = CropContractFactory(required_kg=Decimal('100.00'), allocated_kg=Decimal('50.00'))
    loan = make_disbursed_loan(contract.crop)
    with pytest.raises(ValueError):
      FarmerContractAllocationService.allocate_farmer(contract.id, loan.farmer, loan, Decimal('-20.00'))

  def test_zero_committed_kg_is_rejected(self):
    contract = CropContractFactory(required_kg=Decimal('100.00'), allocated_kg=Decimal('0'))
    loan = make_disbursed_loan(contract.crop)
    with pytest.raises(ValueError):
      FarmerContractAllocationService.allocate_farmer(contract.id, loan.farmer, loan, Decimal('0.00'))
 
@pytest.mark.django_db(transaction=True)
class TestAllocateFarmerConcurrency:
  def test_concurrent_allocations_cannot_jointly_exceed_required_kg(self):
    contract = CropContractFactory(required_kg=Decimal('100.00'), allocated_kg=Decimal('0'))
    loan_a, loan_b = make_disbursed_loan(contract.crop), make_disbursed_loan(contract.crop)
    barrier = threading.Barrier(2)
    results = Queue()
    def worker(loan):
      barrier.wait()
      try:
        FarmerContractAllocationService.allocate_farmer(contract.id, loan.farmer, loan, Decimal('60.00'))
        results.put('success')
      except ContractFullyAllocatedError:
        results.put('failure')
      finally:
        connections.close_all()
    threads = [threading.Thread(target=worker, args=(loan,)) for loan in (loan_a, loan_b)]
    for t in threads: t.start()
    for t in threads: t.join()
    outcomes = list(results.queue)
    assert outcomes.count('success') == 1, f"expected exactly one to succeed, got: {outcomes}"
    contract.refresh_from_db()
    assert contract.allocated_kg == Decimal('60.00')
 
  def test_two_sequential_allocations_that_exactly_fill_the_contract_both_succeed(self):
    contract = CropContractFactory(required_kg=Decimal('100.00'), allocated_kg=Decimal('0'))
    loan_a, loan_b = make_disbursed_loan(contract.crop), make_disbursed_loan(contract.crop)
    FarmerContractAllocationService.allocate_farmer(contract.id, loan_a.farmer, loan_a, Decimal('50.00'))
    FarmerContractAllocationService.allocate_farmer(contract.id, loan_b.farmer, loan_b, Decimal('50.00'))
    contract.refresh_from_db()
    assert contract.allocated_kg == Decimal('100.00')
    assert contract.status == 'allocated'
    assert FarmerContractAllocation.objects.filter(contract=contract).count() == 2