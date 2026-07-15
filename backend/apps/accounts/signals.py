from django.dispatch import receiver
from django.db.models.signals import post_save
from apps.accounts.models import FarmerProfile, LandownerProfile, BankProfile, FactoryProfile, ShopkeeperProfile, InsuranceProfile, User
from apps.wallets.services import WalletService
from apps.community.models import NumberdarProfile

PROFILE_MAP = {
  'smallholder': FarmerProfile,
  'tenant': FarmerProfile,
  'landowner': LandownerProfile,
  'bank': BankProfile,
  'factory': FactoryProfile,
  'shopkeeper': ShopkeeperProfile,
  'insurance': InsuranceProfile,
  'numberdar': NumberdarProfile,
}

WALLET_TYPE_MAP = {
  'smallholder': 'farmer',
  'tenant': 'farmer',
  'landowner': 'landowner',
  'shopkeeper': 'shopkeeper',
  'bank': 'bank',
}

@receiver(post_save, sender=User)
def create_role_profile(sender, instance, created, **kwargs):
  if not created:
    return
  
  profile_class = PROFILE_MAP.get(instance.role)
  if profile_class:
    profile_class.objects.get_or_create(user=instance)
      
  wallet_type = WALLET_TYPE_MAP.get(instance.role)
  if wallet_type:
    WalletService.create_wallet_for_user(instance, wallet_type)