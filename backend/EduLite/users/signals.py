# users/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile, ProfileFriendRequest

User = get_user_model()


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
    """
    if created:
        # Import here to avoid circular imports
        from notifications.models import Notification

        Notification.objects.create(
            recipient=instance.receiver.user,
            actor=instance.sender.user,
            verb="sent you a friend request",
            notification_type="FRIEND_REQUEST",
            target=instance
        )
