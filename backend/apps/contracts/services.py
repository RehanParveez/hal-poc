from django.db import transaction
from apps.contracts.models import CropContract, FarmerContractAllocation
from shared.exceptions import ContractFullyAllocatedError

class CropContractService:

  @staticmethod
  def create_contract(factory_profile, validated_data):
    with transaction.atomic():
      contract = CropContract.objects.create(factory=factory_profile, **validated_data)
      return contract

  @staticmethod
  def close_contract_if_full(contract):
    if contract.allocated_kg >= contract.required_kg:
      contract.status = 'allocated'
      contract.save(update_fields=['status'])

class FarmerContractAllocationService:

  @staticmethod
  def allocate_farmer(contract_id, farmer_profile, loan, committed_kg):
    with transaction.atomic():
      contract = CropContract.objects.select_for_update().get(id=contract_id)
      if contract.status != 'open':
        raise ValueError(f"the contract is not open for alloca. Current status: {contract.status}.")
      if loan.farmer != farmer_profile:
        raise PermissionError("the loan doesnt belong to you.")
      if loan.status != 'disbursed':
        raise ValueError(f"the loan s/h be disbursed before alloca. to a contract. Current status: {loan.status}.")
      if loan.crop != contract.crop:
        raise ValueError(f"your loan is for {loan.crop.code} but this contr is for {contract.crop.code}.")
      if FarmerContractAllocation.objects.filter(contract=contract, farmer=farmer_profile).exists():
        raise ValueError("you are already allocated to this contract.")
      remaining_kg = contract.required_kg - contract.allocated_kg
      if committed_kg > remaining_kg:
        raise ContractFullyAllocatedError(requested=committed_kg, available=remaining_kg)
    
      allocation = FarmerContractAllocation.objects.create(contract=contract, farmer=farmer_profile, loan=loan, committed_kg=committed_kg)
      contract.allocated_kg += committed_kg
      contract.save(update_fields=['allocated_kg'])
      CropContractService.close_contract_if_full(contract)

      return allocation