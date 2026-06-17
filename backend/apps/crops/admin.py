from django.contrib import admin
from apps.crops.models import CropType, CropInputCap, CropLifecycleMilestone

@admin.register(CropType)
class CropTypeAdmin(admin.ModelAdmin):
  list_display = ('name', 'code', 'season')
  search_fields = ('name', 'code')
  list_filter = ('season',)

@admin.register(CropInputCap)
class CropInputCapAdmin(admin.ModelAdmin):
  list_display = ('crop', 'district', 'input_category', 'max_cost_per_acre', 'valid_season')
  search_fields = ('district', 'valid_season')
  list_filter = ('input_category', 'valid_season')

@admin.register(CropLifecycleMilestone)
class CropLifecycleMilestoneAdmin(admin.ModelAdmin):
  list_display = ('crop', 'phase_number', 'phase_name', 'day_offset', 'unlock_pct', 'allowed_input_categories')
  search_fields = ('phase_name',)
  list_filter = ('crop',)