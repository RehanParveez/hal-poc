import sys
import os
import django

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from decimal import Decimal
from shared.constants import PUNJAB_DISTRICTS
from apps.crops.models import CropType
from apps.crops.services import CropInputCapService

BASE_CAPS = {
  'seed': Decimal('4500'), 'fertilizer': Decimal('12000'), 'pesticide': Decimal('6000'),
  'irrigation': Decimal('3500'), 'labour': Decimal('8000'),
}
SEED_DISTRICTS = PUNJAB_DISTRICTS[:6]

def run():
  crops = CropType.objects.all()
  if not crops.exists():
    print("No crop types found — run seed_crop_milestones.py first.")
    return
  count = 0
  for crop in crops:
    for district in SEED_DISTRICTS:
      for category, base_cost in BASE_CAPS.items():
        CropInputCapService.set_cap({'crop': crop, 'district': district, 'input_category': category, 'valid_season': crop.season,
          'max_cost_per_acre': base_cost})
        count += 1
  print(f"Seeded {count} AFO input caps across {crops.count()} crops and {len(SEED_DISTRICTS)} districts.")

if __name__ == '__main__':
    run()