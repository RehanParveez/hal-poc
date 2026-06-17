from django.db import models
from shared.models import BaseModel
from django.contrib.postgres.fields import ArrayField

class CropType(BaseModel):
  name = models.CharField(max_length=150)
  code = models.CharField(max_length=35, unique=True)
  season = models.CharField(max_length=35, choices=[('rabi', 'Rabi'), ('kharif', 'Kharif')])

  class Meta:
    db_table = 'crop_types'

  def __str__(self):
    return f"{self.name} ({self.season})"

class CropInputCap(BaseModel):
  INPUT_CATEGORIES = (
    ('seed', 'Seed'),
    ('fertilizer', 'Fertilizer'),
    ('pesticide', 'Pesticide'),
    ('irrigation', 'Irrigation'),
    ('labour', 'Labour'),
  )
  crop = models.ForeignKey(CropType, on_delete=models.PROTECT, related_name = 'input_caps')
  district = models.CharField(max_length=130)
  input_category = models.CharField(max_length=40, choices=INPUT_CATEGORIES)
  max_cost_per_acre = models.DecimalField(max_digits=10, decimal_places=2)
  valid_season = models.CharField(max_length=40)

  class Meta:
    db_table = 'crop_input_caps'
    unique_together = [['crop', 'district', 'input_category', 'valid_season']]
    indexes = [models.Index(fields=['crop', 'district']), models.Index(fields=['input_category'])]

  def __str__(self):
    return f"{self.district}"

class CropLifecycleMilestone(BaseModel):
  crop = models.ForeignKey(CropType, on_delete=models.PROTECT, related_name = 'milestones')
  phase_number = models.PositiveSmallIntegerField() 
  phase_name = models.CharField(max_length=150)
  day_offset = models.PositiveIntegerField()
  unlock_pct = models.DecimalField(max_digits=10, decimal_places=2)
  allowed_input_categories = ArrayField(models.CharField(max_length=40))

  class Meta:
    db_table = 'crop_lifecycle_milestones'
    ordering = ['phase_number']
    unique_together = [['crop', 'phase_number']]

  def __str__(self):
    return f"{self.crop.code}"