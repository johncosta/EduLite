# users/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create or update the user profile.
    - Creates a UserProfile instance when a new User instance is created.
    """
    if created:
        UserProfile.objects.create(user=instance)
