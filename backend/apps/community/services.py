import logging
from apps.community.models import NumberdarProfile, FarmerVerificationRequest
from shared.exceptions import OutOfJurisdictionError, DuplicateVerificationRequestError
from django.db import transaction
from apps.notifications.services import NotificationService
from django.utils import timezone
from django.conf import settings
from apps.accounts.models import User

logger = logging.getLogger(__name__)

class NumberdarVerificationService:

  @staticmethod
  def submit_verification_request(farmer_profile, numberdar_id):
    numberdar = NumberdarProfile.objects.select_related('user').get(id=numberdar_id, is_active=True)
    if farmer_profile.user.district != numberdar.jurisdiction_district:
      raise OutOfJurisdictionError(farmer_district=farmer_profile.user.district, numberdar_district=numberdar.jurisdiction_district)

    already_active = FarmerVerificationRequest.objects.filter(farmer=farmer_profile, status__in=['pending', 'approved']).exists()
    if already_active:
      raise DuplicateVerificationRequestError()

    with transaction.atomic():
      req = FarmerVerificationRequest.objects.create(farmer=farmer_profile, numberdar=numberdar, status = 'pending')

    transaction.on_commit(lambda: NotificationService.notify(numberdar.user, 'verification_request_received',
      {'farmer_name': farmer_profile.user.full_name, 'farmer_district': farmer_profile.user.district},
      reference_id=req.id))
    return req

  @staticmethod
  def approve_farmer(request_id, numberdar_user):
    with transaction.atomic():
      req = FarmerVerificationRequest.objects.select_for_update().select_related('farmer__user', 'numberdar').get(id=request_id)
      if req.numberdar.user != numberdar_user:
        raise PermissionError("you can only act on verification requests assigned to you.")
      if req.status != 'pending':
        raise ValueError(f"cant approve a request with status '{req.status}'. only pending requests can be approved.")

      req.status = 'approved'
      req.resolved_at = timezone.now()
      req.save(update_fields=['status', 'resolved_at'])

      req.farmer.user.numberdar_verified = True
      req.farmer.user.save(update_fields=['numberdar_verified'])

      req.numberdar.total_farmers_verified += 1
      req.numberdar.save(update_fields=['total_farmers_verified'])

    transaction.on_commit(lambda: NotificationService.notify(req.farmer.user, 'numberdar_approved', {}, reference_id=req.id))
    return req

  @staticmethod
  def reject_farmer(request_id, numberdar_user, notes=''):
    with transaction.atomic():
      req = FarmerVerificationRequest.objects.select_for_update().select_related('farmer__user', 'numberdar').get(id=request_id)
      if req.numberdar.user != numberdar_user:
        raise PermissionError("you can only act on verification requests assigned to you.")
      if req.status != 'pending':
        raise ValueError(f"can't reject a request with status '{req.status}'. only the pending requests can be rejected.")

      req.status = 'rejected'
      req.numberdar_notes = notes
      req.resolved_at = timezone.now()
      req.save(update_fields=['status', 'numberdar_notes', 'resolved_at'])

    transaction.on_commit(lambda: NotificationService.notify(
      req.farmer.user, 'numberdar_rejected', {'numberdar_notes': notes or 'No reason provided.'}, reference_id=req.id))
    return req

  @staticmethod
  def escalate_timed_out_requests():
    timeout_days = getattr(settings, 'NUMBERDAR_APPROVAL_TIMEOUT_DAYS', 7)
    cutoff = timezone.now() - timezone.timedelta(days=timeout_days)
    admin = User.objects.filter(role='admin').first()

    stale = FarmerVerificationRequest.objects.filter(status = 'pending', submitted_at__lt=cutoff)
    count = 0
    for req in stale:
      req.status = 'escalated'
      req.escalated_to = admin
      req.save(update_fields=['status', 'escalated_to'])
      if admin:
        NotificationService.notify(admin, 'verification_escalated',
          {'farmer_name': req.farmer.user.full_name, 'numberdar_name': req.numberdar.user.full_name}, reference_id=req.id)
      count += 1
    logger.info(f"Escalated {count} stale verification requests.")
    return count