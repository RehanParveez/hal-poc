from django.db import transaction
from apps.land.models import Land, TenantAgreement
from shared.exceptions import AcreageCeilingExceededError
from django.utils import timezone
from apps.notifications.services import NotificationService

class LandService:
  @staticmethod
  def create_parcel(landowner_profile, validated_data):
    with transaction.atomic():
      parcel = Land.objects.create(landowner=landowner_profile, **validated_data)
      landowner_profile.total_registered_acres += parcel.total_acres
      landowner_profile.save(update_fields=['total_registered_acres'])
      return parcel

class TenantAgreementService:
  @staticmethod
  def create_agreement(tenant_profile, parcel_id, validated_data):
    with transaction.atomic():
      parcel = Land.objects.select_for_update().get(id=parcel_id)
      leased_acres = validated_data.get('leased_acres')
      if leased_acres > parcel.available_acres:
        raise AcreageCeilingExceededError(requested=leased_acres, available=parcel.available_acres)
      return TenantAgreement.objects.create(tenant=tenant_profile, parcel=parcel, **validated_data)

  @staticmethod
  def approve_agreement(agreement_id, landowner_profile):
    with transaction.atomic():
      agreement = TenantAgreement.objects.select_for_update().get(id=agreement_id)
      if agreement.parcel.landowner_id != landowner_profile.id:
        raise PermissionError('you dont own this parcel & so cant appr this agreem.')
      if agreement.status != 'pending':
        raise ValueError(f"cant appr an agreem with status '{agreement.status}'. only the pend agreems can be approv.")
      agreement.landowner_approved = True
      agreement.status = 'active'
      agreement.approved_at = timezone.now()
      agreement.save(update_fields=['landowner_approved', 'status', 'approved_at'])
      transaction.on_commit(lambda: NotificationService.notify(agreement.tenant.user, 'agreement_approved',
       {'agreement_type': agreement.agreement_type, 'leased_acres': agreement.leased_acres}, reference_id=agreement.id))
      return agreement

  @staticmethod
  def reject_agreement(agreement_id, landowner_profile, reason=''):
    with transaction.atomic():
      agreement = TenantAgreement.objects.select_for_update().get(id=agreement_id)
      if agreement.parcel.landowner_id != landowner_profile.id:
        raise PermissionError('You dont own this parcel & so cant reject this agreem.')
      if agreement.status != 'pending':
        raise ValueError(f"cant reje an agreem with status '{agreement.status}'.")
      agreement.status = 'rejected'
      agreement.landowner_approved = False
      agreement.rejected_reason = reason
      agreement.save(update_fields=['status', 'landowner_approved', 'rejected_reason'])
      transaction.on_commit(lambda: NotificationService.notify(agreement.tenant.user, 'agreement_rejected',
        {'rejected_reason': reason or 'No reason provided.'}, reference_id=agreement.id))
      return agreement