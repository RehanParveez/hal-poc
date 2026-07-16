import sys
import os
import django
from shared.constants import PUNJAB_DISTRICTS
from apps.accounts.models import User

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

SEED_DISTRICTS = PUNJAB_DISTRICTS[:6]

def run():
  for i, district in enumerate(SEED_DISTRICTS, start=1):
    phone = f"0300000{i:04d}"
    user, created = User.objects.get_or_create(phone=phone, defaults={'cnic': f"35202{i:08d}1",
      'full_name': f"Numberdar — {district}",
      'role': 'numberdar', 'district': district, 'province': 'punjab'})
    if created:
      user.set_password('testpass123')
      user.save()
    profile = user.numberdar_profile
    profile.jurisdiction_district = district
    profile.jurisdiction_villages = [f"{district} Village {n}" for n in range(1, 4)]
    profile.cnic_verified = True
    profile.is_active = True
    profile.save(update_fields=['jurisdiction_district', 'jurisdiction_villages', 'cnic_verified', 'is_active'])
    print(f"{'Created' if created else 'Confirmed'} Numberdar for {district} ({phone} / testpass123)")

if __name__ == '__main__':
    run()