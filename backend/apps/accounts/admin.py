from django.contrib import admin
from apps.accounts.models import User, FarmerProfile, LandownerProfile, BankProfile, FactoryProfile, ShopkeeperProfile, InsuranceProfile

class FarmerProfileInline(admin.StackedInline):
  model = FarmerProfile
  can_delete = False

class LandownerProfileInline(admin.StackedInline):
  model = LandownerProfile
  can_delete = False

class BankProfileInline(admin.StackedInline):
  model = BankProfile
  can_delete = False

class FactoryProfileInline(admin.StackedInline):
  model = FactoryProfile
  can_delete = False

class ShopkeeperProfileInline(admin.StackedInline):
  model = ShopkeeperProfile
  can_delete = False

class InsuranceProfileInline(admin.StackedInline):
  model = InsuranceProfile
  can_delete = False

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
  inlines = [FarmerProfileInline, LandownerProfileInline, BankProfileInline, FactoryProfileInline, ShopkeeperProfileInline,
    InsuranceProfileInline]
  list_display = ['id', 'phone', 'cnic', 'full_name', 'role', 'district', 'province', 'is_verified', 'is_active', 'is_staff', 'numberdar_verified', 'credit_tier', 'secp_verified', 'ntn_verified', 'created_at']
  list_editable = ['secp_verified', 'ntn_verified']
  search_fields = ['phone', 'cnic', 'full_name']
  list_filter = ['role', 'province', 'district', 'is_verified', 'is_active', 'secp_verified']

@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
  list_display = ['id', 'user', 'total_owned_acres', 'arazi_ref']
  search_fields = ('user__full_name', 'user__phone')

@admin.register(LandownerProfile)
class LandownerProfileAdmin(admin.ModelAdmin):
  list_display = ['id', 'user', 'total_registered_acres']
  search_fields = ('user__full_name',)

@admin.register(BankProfile)
class BankProfileAdmin(admin.ModelAdmin):
  list_display = ['id', 'user', 'institution_name', 'branch_code']
  search_fields = ('institution_name', 'user__full_name')

@admin.register(FactoryProfile)
class FactoryProfileAdmin(admin.ModelAdmin):
  list_display = ['id', 'user', 'factory_name', 'ntn_number']
  search_fields = ('factory_name', 'user__full_name')

@admin.register(ShopkeeperProfile)
class ShopkeeperProfileAdmin(admin.ModelAdmin):
  list_display = ['id', 'user', 'shop_name', 'ntn_number']
  search_fields = ('shop_name', 'user__full_name')

@admin.register(InsuranceProfile)
class InsuranceProfileAdmin(admin.ModelAdmin):
  list_display = ['id', 'user', 'company_name']
  search_fields = ('company_name', 'user__full_name')