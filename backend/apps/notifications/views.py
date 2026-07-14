from rest_framework import viewsets
from apps.notifications.serializers import NotificationSerializer
from rest_framework.permissions import IsAuthenticated
from apps.notifications.models import Notification
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
  serializer_class = NotificationSerializer
  permission_classes = [IsAuthenticated]

  def get_queryset(self):
    return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

  @action(detail=False, methods=['get'])
  def unread_count(self, request):
    count = self.get_queryset().filter(is_read=False).count()
    return Response({'unread_count': count})

  @action(detail=True, methods=['patch'])
  def mark_read(self, request, pk=None):
    notif = self.get_object()
    if not notif.is_read:
      notif.is_read = True
      notif.read_at = timezone.now()
      notif.save(update_fields=['is_read', 'read_at'])
    return Response(NotificationSerializer(notif).data)

  @action(detail=False, methods=['patch'])
  def mark_all_read(self, request):
    self.get_queryset().filter(is_read=False).update(is_read=True, read_at=timezone.now())
    return Response({'message': 'All notifications marked as read.'})