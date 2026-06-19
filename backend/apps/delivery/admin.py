from django.contrib import admin
from apps.delivery.models import BatchDelivery

@admin.register(BatchDelivery)
class BatchDeliveryAdmin(admin.ModelAdmin):
  list_display = ('id', 'allocation', 'batch_kg', 'status', 'expected_payout', 'actual_payout', 'delivered_at')
  list_filter = ('status', 'grade_received', 'delivered_at', 'grade_confirmed_at')
  search_fields = ('id', 'allocation__id', 'grade_received', 'grade_notes')
  readonly_fields = ('created_at', 'updated_at')
  ordering = ('-delivered_at',)

  fieldsets = (('Delivery Info', {'fields': ('allocation', 'batch_kg', 'status')}), ('Financials', {'fields': ('expected_payout', 'actual_payout')}),
    ('Grading/QC', {'fields': ('grade_received', 'grade_deduction_pct', 'grade_notes')}),
    ('Timestamps', {'fields': ('delivered_at', 'grade_confirmed_at', 'created_at', 'updated_at'), 'classes': ('collapse',)}))