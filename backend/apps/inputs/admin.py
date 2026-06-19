from django.contrib import admin
from apps.inputs.models import InputSupplyRequest
 
@admin.register(InputSupplyRequest)
class InputSupplyRequestAdmin(admin.ModelAdmin):
  list_display = ['escrow', 'shopkeeper', 'input_category', 'requested_amount', 'status', 'created_at']
  list_filter = ['input_category', 'status']
  search_fields = ['escrow__loan__farmer__user__full_name', 'shopkeeper__shop_name']
  readonly_fields = ['id', 'afo_cap_at_time', 'created_at', 'updated_at']
  ordering = ['-created_at']