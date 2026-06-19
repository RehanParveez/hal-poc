from django.contrib import admin
from apps.contracts.models import CropContract, FarmerContractAllocation

@admin.register(CropContract)
class CropContractAdmin(admin.ModelAdmin):
  list_display = ('factory', 'crop', 'required_kg', 'allocated_kg', 'remaining_kg', 'base_price_per_kg', 'status', 'delivery_deadline')
  list_filter = ('status', 'crop', 'factory')
  search_fields = ('factory__factory_name', 'crop__name')
  readonly_fields = ('allocated_kg',)

@admin.register(FarmerContractAllocation)
class FarmerContractAllocationAdmin(admin.ModelAdmin):
  list_display = ('farmer', 'contract', 'loan', 'committed_kg')
  list_filter = ('contract', 'farmer')
  search_fields = ('farmer__user__full_name', 'contract__factory__factory_name')
  autocomplete_fields = ('contract', 'farmer', 'loan')