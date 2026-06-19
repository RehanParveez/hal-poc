from django.db import transaction
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone
from apps.delivery.models import BatchDelivery

class BatchDeliveryService:

  @staticmethod
  def log_delivery(farmer_profile, allocation, batch_kg):
    with transaction.atomic():
      if allocation.farmer != farmer_profile:
        raise PermissionError("this alloca does not belong to you.")

      already_delivered = allocation.batches.aggregate(total=Sum('batch_kg'))['total'] or Decimal('0')
      if (already_delivered + batch_kg) > allocation.committed_kg:
        raise ValueError(f"cant deliver {batch_kg}kg. You committed {allocation.committed_kg}kg "
          f"and have already delivered {already_delivered}kg.")
      expected_payout = (batch_kg * allocation.contract.base_price_per_kg).quantize(Decimal('0.01'))

      batch = BatchDelivery.objects.create(allocation=allocation, batch_kg=batch_kg, expected_payout=expected_payout, status='in_transit', delivered_at=timezone.now())
      return batch

  @staticmethod
  def mark_received(batch_id, factory_profile):
    with transaction.atomic():
      batch = BatchDelivery.objects.select_for_update().get(id=batch_id)
      if batch.allocation.contract.factory != factory_profile:
        raise PermissionError("this batch doesn't belong to your contract.")
      if batch.status != 'in_transit':
        raise ValueError(f"only in_transit batches can be marked receiv. Current status: {batch.status}.")
      batch.status = 'received'
      batch.save(update_fields=['status'])
      return batch

  @staticmethod
  def confirm_grade(batch_id, factory_profile, grade_received, grade_deduction_pct, grade_notes=''):
    with transaction.atomic():
      batch = BatchDelivery.objects.select_for_update().get(id=batch_id)
      if batch.allocation.contract.factory != factory_profile:
        raise PermissionError("this batch does not belong to your contract.")
      if batch.status not in ('in_transit', 'received'):
        raise ValueError(f"cant confirm the grade on a batch with status '{batch.status}'.")
      deduction_multiplier = (Decimal('100') - grade_deduction_pct) / Decimal('100')
      actual_payout = (batch.expected_payout * deduction_multiplier).quantize(Decimal('0.01'))

      batch.grade_received = grade_received
      batch.grade_deduction_pct = grade_deduction_pct
      batch.grade_notes = grade_notes
      batch.actual_payout = actual_payout
      batch.status = 'grade_confirmed'
      batch.grade_confirmed_at = timezone.now()
      batch.save(update_fields=['grade_received', 'grade_deduction_pct', 'grade_notes', 'actual_payout', 'status', 'grade_confirmed_at'])

      return batch