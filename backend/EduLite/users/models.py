from django.db import models
from django.contrib.auth import get_user_model
from .models_choices import OCCUPATION_CHOICES, COUNTRY_CHOICES, LANGUAGE_CHOICES

User = get_user_model()

class UserProfile(models.Model):
    # The signal in signals.py will create a UserProfile instance when a new User is created
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True, max_length=1000)
    occupation = models.CharField(
        max_length=64,
        choices=OCCUPATION_CHOICES,
        blank=True,
        null=True
    )
    country = models.CharField(
        max_length=64,
        choices=COUNTRY_CHOICES,
        blank=True,
        null=True
    )
    # the website can load auto-translated based on preferred language
    preferred_language = models.CharField(
        max_length=64,
        choices=LANGUAGE_CHOICES,
        blank=True,
        null=True
    )
    # secondary language to fall back on
    secondary_language = models.CharField(
        max_length=64,
        choices=LANGUAGE_CHOICES,
        blank=True,
        null=True
    )
    picture = models.ImageField(upload_to='profile_pics', blank=True, null=True) # Added null=True
    website_url = models.URLField(max_length=200, blank=True, null=True)

    friends = models.ManyToManyField(User, related_name='friend_profiles', blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    
class ProfileFriendRequest(models.Model):
    """
    Represents a friend request sent from one UserProfile to another.
    """
    sender = models.ForeignKey(
        'UserProfile',  # Use string 'UserProfile' to handle potential forward reference
        on_delete=models.CASCADE,
        related_name='sent_friend_requests'
    )
    receiver = models.ForeignKey(
        'UserProfile',  # Use string 'UserProfile'
        on_delete=models.CASCADE,
        related_name='received_friend_requests'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the friend request was sent."
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['sender', 'receiver'],
                name='unique_pending_friend_request'
            )
        ]
        ordering = ['-created_at']
        verbose_name = "Profile Friend Request"
        verbose_name_plural = "Profile Friend Requests"

    def __str__(self):
        return f"Friend request from {self.sender.user.username} to {self.receiver.user.username}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.sender == self.receiver:
            raise ValidationError("Cannot send a friend request to oneself.")
        super().clean()

    def accept(self):
        """
        Accepts the friend request.
        Adds sender and receiver to each other's friends list and deletes the request.
        """
        if self.sender and self.receiver: # Ensure sender and receiver profiles exist
            self.receiver.friends.add(self.sender.user) # Assuming 'friends' is on UserProfile, links to User
            self.sender.friends.add(self.receiver.user) # Assuming 'friends' is on UserProfile, links to User
            self.delete()
            return True
        return False

    def decline(self):
        """
        Declines (deletes) the friend request.
        """
        self.delete()
        return True
