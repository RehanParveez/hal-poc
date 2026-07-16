import sys
import os
import django
from apps.crops.models import CropType
from apps.crops.services import CropLifecycleMilestoneService

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

CROPS = [
  {'name': 'Wheat', 'code': 'WHEAT', 'season': 'rabi'},
  {'name': 'Cotton', 'code': 'COTTON', 'season': 'kharif'},
  {'name': 'Rice', 'code': 'RICE', 'season': 'kharif'},
]

MILESTONES = {
  'WHEAT': [
    {'phase_number': 1, 'phase_name': 'Sowing & Land Preparation', 'day_offset': 0, 'unlock_pct': 30, 'allowed_input_categories': ['seed', 'fertilizer']},
    {'phase_number': 2, 'phase_name': 'Vegetative Growth', 'day_offset': 30, 'unlock_pct': 25, 'allowed_input_categories': ['fertilizer', 'pesticide', 'irrigation']},
    {'phase_number': 3, 'phase_name': 'Flowering & Grain Fill', 'day_offset': 75, 'unlock_pct': 25, 'allowed_input_categories': ['pesticide', 'irrigation']},
    {'phase_number': 4, 'phase_name': 'Pre-Harvest', 'day_offset': 110, 'unlock_pct': 20, 'allowed_input_categories': ['labour']},
  ],
    'COTTON': [
      {'phase_number': 1, 'phase_name': 'Sowing & Land Preparation', 'day_offset': 0, 'unlock_pct': 25, 'allowed_input_categories': ['seed', 'fertilizer']},
      {'phase_number': 2, 'phase_name': 'Vegetative Growth', 'day_offset': 25, 'unlock_pct': 25, 'allowed_input_categories': ['fertilizer', 'pesticide', 'irrigation']},
      {'phase_number': 3, 'phase_name': 'Boll Formation', 'day_offset': 70, 'unlock_pct': 30, 'allowed_input_categories': ['pesticide', 'irrigation']},
      {'phase_number': 4, 'phase_name': 'Picking', 'day_offset': 130, 'unlock_pct': 20, 'allowed_input_categories': ['labour']},
  ],
    'RICE': [
      {'phase_number': 1, 'phase_name': 'Nursery & Transplanting', 'day_offset': 0, 'unlock_pct': 30, 'allowed_input_categories': ['seed', 'fertilizer']},
      {'phase_number': 2, 'phase_name': 'Vegetative Growth', 'day_offset': 25, 'unlock_pct': 25, 'allowed_input_categories': ['fertilizer', 'pesticide', 'irrigation']},
      {'phase_number': 3, 'phase_name': 'Panicle Initiation', 'day_offset': 60, 'unlock_pct': 25, 'allowed_input_categories': ['pesticide', 'irrigation']},
      {'phase_number': 4, 'phase_name': 'Pre-Harvest', 'day_offset': 100, 'unlock_pct': 20, 'allowed_input_categories': ['labour']},
  ],
}

def run():
  crop_lookup = {}
  for c in CROPS:
    crop, created = CropType.objects.update_or_create(code=c['code'], defaults={'name': c['name'], 'season': c['season']})
    crop_lookup[c['code']] = crop
    print(f"{'Created' if created else 'Confirmed'} crop: {crop.name} ({crop.code})")

  for code, phases in MILESTONES.items():
    for phase in phases:
      milestone, created = CropLifecycleMilestoneService.set_milestone({'crop': crop_lookup[code], **phase})
      print(f"  {'Created' if created else 'Updated'} {code} phase {phase['phase_number']}: {phase['phase_name']}")

if __name__ == '__main__':
  run()