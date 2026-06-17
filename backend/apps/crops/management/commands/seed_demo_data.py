from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.crops.models import CropType, CropInputCap, CropLifecycleMilestone

class Command(BaseCommand):
  help = 'Seed POC demo data — users, crops, input caps, milestones'

  def handle(self, *args, **options):
    self._create_users()
    self._create_crops_data()
    self.stdout.write(self.style.SUCCESS('POC demo data seeded successfully.'))

  def _create_users(self):
    users_data = [
      ('03451234567', 'demo1234', 'smallholder', 'Muhammad Akram',     'Sahiwal', '3510198765431'),
      ('03011234567', 'demo1234', 'tenant',      'Ghulam Rasool',      'Sahiwal', '3510198765432'),
      ('03211234567', 'demo1234', 'landowner',   'Chaudhry Zulfiqar',  'Sahiwal', '3510198765433'),
      ('03331234567', 'demo1234', 'bank',        'Tariq Mahmood',      'Sahiwal', '3510198765434'),
      ('03001234567', 'demo1234', 'factory',     'Hussain Agri Mills', 'Sahiwal', '3510198765435'),
      ('03121234567', 'demo1234', 'shopkeeper',  'Khalid Seed Centre', 'Sahiwal', '3510198765436'),
      ('03411234567', 'demo1234', 'afo',         'Rana Sajid Iqbal',   'Sahiwal', '3510198765437'),
      ('03061234567', 'demo1234', 'insurance',   'Salman Takaful Co',  'Sahiwal', '3510198765438'),
    ]
    for phone, pwd, role, name, district, cnic in users_data:
      if not User.objects.filter(phone=phone).exists():
        User.objects.create_user(phone=phone, password=pwd, role=role, full_name=name, district=district, cnic=cnic)
        self.stdout.write(f"  Created {role}: {phone} — {name}")
        
  def _create_crops_data(self):
    wheat, _ = CropType.objects.get_or_create(code='WHEAT', defaults={'name': 'Wheat', 'season': 'rabi'})
    cotton, _ = CropType.objects.get_or_create(code='COTTON', defaults={'name': 'Cotton', 'season': 'kharif'})
    sugarcane, _ = CropType.objects.get_or_create(code='SUGARCANE', defaults={'name': 'Sugarcane', 'season': 'kharif'})

    caps = [
      (wheat,     'Sahiwal', 'seed',        1100, 'Rabi-2025'),
      (wheat,     'Sahiwal', 'fertilizer',  2400, 'Rabi-2025'),
      (wheat,     'Sahiwal', 'pesticide',    750, 'Rabi-2025'),
      (wheat,     'Sahiwal', 'irrigation',   550, 'Rabi-2025'),
      (wheat,     'Sahiwal', 'labour',       950, 'Rabi-2025'),
      (cotton,    'Sahiwal', 'seed',        1750, 'Kharif-2025'),
      (cotton,    'Sahiwal', 'fertilizer',  3100, 'Kharif-2025'),
      (cotton,    'Sahiwal', 'pesticide',   1150, 'Kharif-2025'),
      (cotton,    'Sahiwal', 'irrigation',   700, 'Kharif-2025'),
      (cotton,    'Sahiwal', 'labour',      1200, 'Kharif-2025'),
      (sugarcane, 'Sahiwal', 'seed',        2200, 'Kharif-2025'),
      (sugarcane, 'Sahiwal', 'fertilizer',  3800, 'Kharif-2025'),
      (sugarcane, 'Sahiwal', 'pesticide',    900, 'Kharif-2025'),
      (sugarcane, 'Sahiwal', 'irrigation',  1100, 'Kharif-2025'),
      (sugarcane, 'Sahiwal', 'labour',      1500, 'Kharif-2025'),
    ]
    for crop, district, category, amount, season in caps:
      CropInputCap.objects.get_or_create(crop=crop, district=district, input_category=category,
        valid_season=season, defaults={'max_cost_per_acre': amount})

    wheat_phases = [
      (1, 'Seed Purchase',          0,  25, ['seed']),
      (2, 'Fertilizer Application', 21, 35, ['fertilizer']),
      (3, 'Pesticide Treatment',    50, 25, ['pesticide', 'labour']),
      (4, 'Irrigation and Labour',  75, 15, ['irrigation', 'labour']),
    ]
    for num, name, days, pct, cats in wheat_phases:
      CropLifecycleMilestone.objects.get_or_create(crop=wheat, phase_number=num,
        defaults={'phase_name': name, 'day_offset': days, 'unlock_pct': pct, 'allowed_input_categories': cats})

    cotton_phases = [
      (1, 'Seed Purchase',          0,  20, ['seed']),
      (2, 'Fertilizer Application', 25, 35, ['fertilizer']),
      (3, 'Pesticide Treatment',    55, 30, ['pesticide', 'labour']),
      (4, 'Irrigation and Labour',  80, 15, ['irrigation', 'labour']),
    ]
    for num, name, days, pct, cats in cotton_phases:
      CropLifecycleMilestone.objects.get_or_create(crop=cotton, phase_number=num,
        defaults={'phase_name': name, 'day_offset': days, 'unlock_pct': pct, 'allowed_input_categories': cats})

    self.stdout.write('  Wheat, Cotton and Sugarcane seeded with caps and milest.')