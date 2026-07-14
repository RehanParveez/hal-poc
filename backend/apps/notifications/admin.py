from django.contrib import admin
from apps.notifications.models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
  list_display = ('recipient', 'event_type', 'channel', 'status', 'is_read', 'created_at')
  list_filter = ('status', 'channel', 'event_type', 'is_read', 'created_at')
  search_fields = ('recipient__phone', 'recipient__full_name', 'subject', 'message', 'reference_id')
  date_hierarchy = 'created_at'
  readonly_fields = ('created_at', 'updated_at',  'sent_at', 'read_at', 'reference_id')

  fieldsets = (('Recipient & Routing', {'fields': ('recipient', 'channel')}),      
    ('Event Details', {'fields': ('event_type', 'reference_id', 'subject', 'message')}),
    ('Delivery Status', {'fields': ('status', 'error_message', 'is_read')}),
    ('Timestamps', {'fields': ('sent_at', 'read_at', 'created_at', 'updated_at'), 'classes': ('collapse',)
    }),
   )