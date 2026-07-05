import pytest
from decimal import Decimal
from shared.exceptions import AFOLimitExceededError, NotEnoughEscrowError, WrongPhaseForCategoryError, AcreageCeilingExceededError, LoanAlreadyDisbursedError, NoActivePhaseError, ContractFullyAllocatedError, custom_exception_handler

class TestAFOLimitExceededErrorComputation:
  def test_remaining_allowed_normal_case(self):
    exc = AFOLimitExceededError(category = "fertilizer", requested=Decimal("300"), cap_total=Decimal("1000"), already_spent=Decimal("800"))
    assert exc.remaining_allowed == Decimal("200")

  def test_remaining_allowed_goes_negative_when_already_overspent(self):
    exc = AFOLimitExceededError(category = "seed", requested=Decimal("50"), cap_total=Decimal("1000"), already_spent=Decimal("1200"))
    assert exc.remaining_allowed == Decimal("-200")

class TestCustomExceptionHandler:
  def test_afo_limit_exceeded_clamps_remaining_to_zero_in_response(self):
    exc = AFOLimitExceededError(category = "fertilizer", requested=Decimal("300"), cap_total=Decimal("1000"), already_spent=Decimal("1200"))
    response = custom_exception_handler(exc, context={})
    assert response.status_code == 400
    assert response.data['error'] == 'AFO_LIMIT_EXCEEDED'
    assert response.data['remaining_allowed'] == '0'

  def test_not_enough_escrow_returns_400(self):
    exc = NotEnoughEscrowError(requested=Decimal("500"), available=Decimal("100"))
    response = custom_exception_handler(exc, context={})
    assert response.status_code == 400
    assert response.data['error'] == 'INSUFFICIENT_ESCROW'
    assert response.data['available'] == '100'

  def test_wrong_phase_for_category_returns_400_with_allowed_list(self):
    exc = WrongPhaseForCategoryError(requested_category = "fertilizer", current_phase_name = "harvest", allowed_categories=["labor", "transport"])
    response = custom_exception_handler(exc, context={})
    assert response.status_code == 400
    assert response.data['error'] == 'INVALID_PHASE_FOR_CATEGORY'
    assert response.data['allowed_categories'] == ["labor", "transport"]

  def test_acreage_ceiling_exceeded_returns_400(self):
    exc = AcreageCeilingExceededError(requested=Decimal("12.5"), available=Decimal("8"))
    response = custom_exception_handler(exc, context={})
    assert response.status_code == 400
    assert response.data['error'] == 'ACREAGE_CEILING_EXCEEDED'

  def test_loan_already_disbursed_returns_409_not_400(self):
    response = custom_exception_handler(LoanAlreadyDisbursedError(), context={})
    assert response.status_code == 409
    assert response.data['error'] == 'LOAN_ALREADY_DISBURSED'

  def test_contract_fully_allocated_returns_409(self):
    exc = ContractFullyAllocatedError(requested=Decimal("500"), available=Decimal("100"))
    response = custom_exception_handler(exc, context={})
    assert response.status_code == 409
    assert response.data['error'] == 'CONTRACT_FULLY_ALLOCATED'

  def test_no_active_phase_error_is_currently_unhandled(self):
    response = custom_exception_handler(NoActivePhaseError(), context={})
    assert response is not None, (
      "NoActivePhaseError has no branch in custom_exception_handler -- "
      "it will leak as a raw 500 instead of a clean error response")
    assert response.status_code == 400

  def test_unrelated_exception_falls_through_untouched(self):
    response = custom_exception_handler(ValueError("unrelated"), context={})
    assert response is None

@pytest.mark.parametrize("exc", [AFOLimitExceededError(category = "c", requested=1, cap_total=10, already_spent=5),
  NotEnoughEscrowError(requested=1, available=0), WrongPhaseForCategoryError(requested_category="c", current_phase_name = "p", allowed_categories=["a"]),
    AcreageCeilingExceededError(requested=1, available=0), ContractFullyAllocatedError(requested=1, available=0), LoanAlreadyDisbursedError(),
    NoActivePhaseError()])

def test_exception_has_non_empty_string_representation(exc):
  assert str(exc) != "", f"{type(exc).__name__} produces an empty str() -- add a super().__init__() message"