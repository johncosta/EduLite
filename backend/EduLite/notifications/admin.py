from django.contrib import admin
from .models import Notification

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'notification_type', 'is_read', 'created_at')
    list_filter = ('is_read', 'recipient', 'created_at')

admin.site.register(Notification, NotificationAdmin)
