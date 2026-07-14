from rest_framework import serializers
from apps.notifications.models import Notification

class NotificationSerializer(serializers.ModelSerializer):
  class Meta:
    model = Notification
    fields = ['id', 'event_type', 'channel', 'subject', 'message', 'reference_id', 'status', 'is_read', 'created_at', 'read_at']
    read_only_fields = fields