# users/tests/test_profiles.py

from pathlib import Path
from django.conf import settings

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError # For testing OneToOne uniqueness
from django.core.files.uploadedfile import SimpleUploadedFile # For ImageField testing

from ..models import UserProfile # Assuming models.py is in the same 'users' app
# Import your choices if you need to explicitly test setting them
from ..models_choices import OCCUPATION_CHOICES, COUNTRY_CHOICES, LANGUAGE_CHOICES

User = get_user_model()

class TestUserProfileModel(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create a user. The signal should automatically create a UserProfile.
        cls.user1 = User.objects.create_user(
            username='testuser1',
            password='password123',
            email='testuser1@example.com'
        )
        cls.user2 = User.objects.create_user(
            username='testuser2',
            password='password123',
            email='testuser2@example.com'
        )
        # cls.user1.profile should exist due to the signal
        # cls.user2.profile should also exist

    def test_profile_auto_creation_on_user_create(self):
        """Test that a UserProfile is automatically created when a User is created."""
        self.assertTrue(hasattr(self.user1, 'profile'))
        self.assertIsInstance(self.user1.profile, UserProfile)
        self.assertEqual(self.user1.profile.user, self.user1)

        # Ensure it's a true OneToOne and another profile can't be created for the same user manually
        # (though the signal handles creation, this tests the OneToOne integrity)
        with self.assertRaises(IntegrityError): # Or a more specific error if UserProfile.user is primary_key
             # This might raise an error if userprofile.user is the PK, or if it's just unique.
             self.user1.profile = UserProfile(user=self.user1)
             self.user1.profile.save()

    def test_profile_str_representation(self):
        """Test the __str__ method of the UserProfile."""
        profile = self.user1.profile
        self.assertEqual(str(profile), f"{self.user1.username}'s Profile")

    def test_profile_default_blank_null_fields(self):
        """Test that fields that can be blank/null are indeed so by default."""
        profile = self.user1.profile
        self.assertEqual(profile.bio, None) # Or "" if you change null=True to default=""
        self.assertEqual(profile.occupation, None)
        self.assertEqual(profile.country, None)
        self.assertEqual(profile.preferred_language, None)
        self.assertEqual(profile.secondary_language, None)
        self.assertEqual(profile.picture, None) # Or "" if ImageField defaults to empty string
        self.assertEqual(profile.friends.count(), 0)

    def test_profile_can_save_choices_fields(self):
        """Test saving valid choices to choice fields."""
        profile = self.user1.profile
        profile.occupation = OCCUPATION_CHOICES[0][0] # Save the first value of occupation choices
        profile.country = COUNTRY_CHOICES[0][0]
        profile.preferred_language = LANGUAGE_CHOICES[0][0]
        profile.save()

        updated_profile = UserProfile.objects.get(user=self.user1)
        self.assertEqual(updated_profile.occupation, OCCUPATION_CHOICES[0][0])
        self.assertEqual(updated_profile.country, COUNTRY_CHOICES[0][0])
        self.assertEqual(updated_profile.preferred_language, LANGUAGE_CHOICES[0][0])

    def test_profile_picture_field(self):
        """Test assigning and saving an ImageField."""
        profile = self.user1.profile
        # Create a dummy image file for testing
        # Note: This doesn't test actual image processing, just that the field can store a file path.
        dummy_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'', # Empty content for dummy file
            content_type='image/jpeg'
        )
        profile.picture = dummy_image
        profile.save()

        updated_profile = UserProfile.objects.get(user=self.user1)
        self.assertTrue(updated_profile.picture.name.startswith('profile_pics/test_image'))
        # Clean up the dummy file if it was actually saved to disk
        # (Django's test runner often handles media file cleanup in a test-specific media root)
        if updated_profile.picture:
            full_picture_path = settings.MEDIA_ROOT / updated_profile.picture.name

            if full_picture_path.exists():
                full_picture_path.unlink(missing_ok=True)

    def test_profile_friends_relationship(self):
        """Test adding, removing, and querying friends."""
        profile1 = self.user1.profile
        profile2 = self.user2.profile # Assuming user2 also has a profile auto-created

        self.assertEqual(profile1.friends.count(), 0)
        self.assertEqual(profile2.friends.count(), 0) # If friends is to User model

        # Add user2 as a friend to user1
        profile1.friends.add(self.user2)
        self.assertEqual(profile1.friends.count(), 1)
        self.assertIn(self.user2, profile1.friends.all())

        # Check the reverse relationship from User model to UserProfile's friends
        # User -> UserProfile (where this user is a friend)
        # self.user2.friend_profiles will give UserProfiles that list user2 as a friend.
        self.assertIn(profile1, self.user2.friend_profiles.all())


        # Add user1 as a friend to user2 (for symmetry, if not automatic)
        profile2.friends.add(self.user1)
        self.assertEqual(profile2.friends.count(), 1)
        self.assertIn(self.user1, profile2.friends.all())
        self.assertIn(profile2, self.user1.friend_profiles.all())


        # Remove friend
        profile1.friends.remove(self.user2)
        self.assertEqual(profile1.friends.count(), 0)
        self.assertNotIn(profile1, self.user2.friend_profiles.all()) # Check reverse removal

    def test_profile_max_length_fields(self):
        """Test max_length constraints for CharFields and TextField."""
        profile = self.user1.profile

        profile.bio = 'a' * 1000
        profile.save() # Should save fine

        profile.occupation = 'a' * 64
        profile.save() # Should save fine

        
        self.assertEqual(UserProfile.objects.get(user=self.user1).bio, 'a' * 1000)
        self.assertEqual(UserProfile.objects.get(user=self.user1).occupation, 'a' * 64)


    # You can add more tests:
    # - Test that UserProfile cannot be created without a user (IntegrityError)
    # - Test edge cases for choices if you have validation logic around them in the model.