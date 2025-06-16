# users/signals.py

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile, ProfileFriendRequest

User = get_user_model()

# Set up logger for this module
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create or update the user profile.
    - Creates a UserProfile instance when a new User instance is created.
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=ProfileFriendRequest)
def create_notification_on_friend_request(sender, instance, created, **kwargs):
    """
    Signal handler to create a notification when a friend request is sent.
    - Creates a Notification instance when a new ProfileFriendRequest is created.
    - Handles errors gracefully to prevent breaking the main friend request creation.
    """
    if created:
        try:
            # Import here to avoid circular imports
            from notifications.models import Notification

            Notification.objects.create(
                recipient=instance.receiver.user,
                actor=instance.sender.user,
                verb="sent you a friend request",
                notification_type="FRIEND_REQUEST",
                target=instance
            )
            logger.debug(
                f"Notification created for friend request {instance.id} "
                f"from {instance.sender.user.username} to {instance.receiver.user.username}"
            )
        except Exception as e:
            # Log the error but don't re-raise it to prevent breaking the main operation
            logger.error(
                f"Failed to create notification for friend request {instance.id} "
                f"from {instance.sender.user.username} to {instance.receiver.user.username}: {e}"
            )
