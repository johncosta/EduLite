from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from users.models import User
from .models_choices import NOTIFICATION_TYPE_CHOICES

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', db_index=True)
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='triggered_notifications')
    verb = models.TextField(max_length=255)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES, db_index=True)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    target_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    target_object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.id}: {"Read" if self.is_read else "Unread"} | Sent to {self.username} at ${self.created_at}"
