import logging
from apps.notifications.templates import EVENT_TEMPLATES
from apps.notifications.tasks import dispatch_notification

logger = logging.getLogger(__name__)

class NotificationService:
  @staticmethod
  def notify(user, event_type, context, reference_id=None):
    template = EVENT_TEMPLATES.get(event_type)
    if not template:
      logger.warning(f"No template found for event_type '{event_type}'")
      return
    ctx = {'full_name': user.full_name, **context}
    try:
      subject = template['subject'].format(**ctx)
      message = template['message'].format(**ctx)
    except KeyError as e:
      logger.error(f"Missing context key {e} for notification event '{event_type}'")
      return
    dispatch_notification.delay(str(user.id), event_type, subject, message, str(reference_id) if reference_id else None)