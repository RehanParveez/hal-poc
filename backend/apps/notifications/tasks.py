import logging
from celery import shared_task
from apps.accounts.models import User
from django.core.mail import send_mail
from apps.notifications.models import Notification
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def dispatch_notification(self, user_id, event_type, subject, message, reference_id=None):
  try:
    user = User.objects.get(id=user_id)
  except User.DoesNotExist:
    logger.error(f"notification dispatch failed: User {user_id} not pres")
    return

  if user.email:
    try:
      send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
      Notification.objects.create(recipient=user, event_type=event_type, channel = 'email',
        subject=subject, message=message, reference_id=reference_id, status = 'sent', sent_at=timezone.now())
    except Exception as e:
      Notification.objects.create(recipient=user, event_type=event_type, channel = 'email',
        subject=subject, message=message, reference_id=reference_id, status = 'failed', error_message=str(e))
      raise self.retry(exc=e)
  else:
    logger.warning(f"[SMS STUB] To: {user.phone} | {subject} | {message}")
    Notification.objects.create(recipient=user, event_type=event_type, channel = 'sms',
      subject=subject, message=message, reference_id=reference_id, status = 'stubbed')