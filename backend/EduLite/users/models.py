from django.db import models
from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError


from .models_choices import OCCUPATION_CHOICES, COUNTRY_CHOICES, LANGUAGE_CHOICES

User = get_user_model()


class UserProfile(models.Model):
    # The signal in signals.py will create a UserProfile instance when a new User is created
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, null=True, max_length=1000)
    occupation = models.CharField(
        max_length=64, choices=OCCUPATION_CHOICES, blank=True, null=True
    )
    country = models.CharField(
        max_length=64, choices=COUNTRY_CHOICES, blank=True, null=True
    )
    # the website can load auto-translated based on preferred language
    preferred_language = models.CharField(
        max_length=64, choices=LANGUAGE_CHOICES, blank=True, null=True
    )
    # secondary language to fall back on
    secondary_language = models.CharField(
        max_length=64, choices=LANGUAGE_CHOICES, blank=True, null=True
    )
    picture = models.ImageField(
        upload_to="profile_pics", blank=True, null=True
    )  # Added null=True
    website_url = models.URLField(max_length=200, blank=True, null=True)

    friends = models.ManyToManyField(User, related_name="friend_profiles", blank=True)

    def __str__(self):
        ret_str = f"{self.user.username}"
        if self.user.first_name and self.user.last_name:
            ret_str += f" {self.user.first_name} {self.user.last_name}"
        elif self.user.first_name:
            ret_str += f" ({self.user.first_name})"
        elif self.user.last_name:
            ret_str += f" {self.user.last_name}"
        return f"{ret_str}"


# Example of how to get friend requests from a UserProfile:
# received_requests = my_profile.received_friend_requests.all()
# sent_requests = my_profile.sent_friend_requests.all()


class ProfileFriendRequest(models.Model):
    """
    Represents a friend request sent from one UserProfile to another.

    Methods:

    - accept(): Accepts the friend request. Deletes the request.
    - decline(): Declines the friend request. Deletes the request.
    """

    sender = models.ForeignKey(
        "UserProfile", on_delete=models.CASCADE, related_name="sent_friend_requests"
    )
    receiver = models.ForeignKey(
        "UserProfile", on_delete=models.CASCADE, related_name="received_friend_requests"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp when the friend request was sent."
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["sender", "receiver"], name="unique_pending_friend_request"
            )
        ]
        ordering = ["-created_at"]
        verbose_name = "Profile Friend Request"
        verbose_name_plural = "Profile Friend Requests"

    def __str__(self):
        return f"Friend request from {self.sender.user.username} to {self.receiver.user.username}"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.sender == self.receiver:
            raise ValidationError("Cannot send a friend request to oneself.")
        # if they are already friends, throw an error
        if self.sender.friends.filter(id=self.receiver.user.id).exists():
            raise ValidationError("Cannot send a friend request to a friend.")
        if self.receiver.friends.filter(id=self.sender.user.id).exists():
            raise ValidationError("Cannot send a friend request to a friend.")
        super().clean()

    def accept(self):
        """
        Accepts the friend request.
        Adds sender and receiver to each other's friends list and deletes the request.
        """
        try:
            with transaction.atomic():
                # Re-fetch with `select_for_update` to guard against races
                req = type(self).objects.select_for_update().get(pk=self.pk)
                req.receiver.friends.add(req.sender.user)
                req.sender.friends.add(req.receiver.user)
                req.delete()
            return True
        except (type(self).DoesNotExist, IntegrityError):
            return False

    def decline(self):
        """
        Declines the friend request.
        Deletes the request.
        """
        try:
            with transaction.atomic():
                # Re-fetch with `select_for_update` to guard against races
                req = type(self).objects.select_for_update().get(pk=self.pk)
                req.delete()
            return True
        except (type(self).DoesNotExist, IntegrityError):
            return False
