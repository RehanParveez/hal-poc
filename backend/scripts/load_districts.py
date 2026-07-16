import os
import sys
import django
from shared.constants import PUNJAB_DISTRICTS

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

if __name__ == '__main__':
  print(f"Canonical district list — {len(PUNJAB_DISTRICTS)} districts:")
  for d in PUNJAB_DISTRICTS:
    print(f"  - {d}")