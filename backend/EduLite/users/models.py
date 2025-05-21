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

    friends = models.ManyToManyField(User, related_name='friend_profiles', blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"