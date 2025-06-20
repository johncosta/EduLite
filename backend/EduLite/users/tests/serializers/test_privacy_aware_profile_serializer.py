# backend/EduLite/users/tests/serializers/test_privacy_aware_profile_serializer.py
# Tests for privacy-aware ProfileSerializer functionality

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request

from users.serializers import ProfileSerializer
from users.models import UserProfile, UserProfilePrivacySettings

User = get_user_model()


class PrivacyAwareProfileSerializerTests(TestCase):
    """
    Test suite for privacy-aware ProfileSerializer functionality.
    Tests profile visibility based on privacy settings and user relationships.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all test methods."""
        # Create users with different privacy levels
        cls.user_public = User.objects.create_user(
            username="public_user",
            first_name="Public",
            last_name="User",
            email="public@example.com"
        )

        cls.user_friends_only = User.objects.create_user(
            username="friends_only_user",
            first_name="Friends",
            last_name="Only",
            email="friends@example.com"
        )

        cls.user_private = User.objects.create_user(
            username="private_user",
            first_name="Private",
            last_name="User",
            email="private@example.com"
        )

        cls.user_friend = User.objects.create_user(
            username="friend_user",
            first_name="Friend",
            last_name="User",
            email="friend@example.com"
        )

        cls.user_stranger = User.objects.create_user(
            username="stranger_user",
            first_name="Stranger",
            last_name="User",
            email="stranger@example.com"
        )

        cls.admin_user = User.objects.create_user(
            username="admin_user",
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            is_staff=True,
            is_superuser=True
        )

        # Set up friendships
        cls.user_friends_only.profile.friends.add(cls.user_friend)
        cls.user_friend.profile.friends.add(cls.user_friends_only)
        cls.user_private.profile.friends.add(cls.user_friend)
        cls.user_friend.profile.friends.add(cls.user_private)

        # Configure privacy settings
        # Public user - public profile
        cls.user_public.profile.privacy_settings.profile_visibility = 'public'
        cls.user_public.profile.privacy_settings.save()

        # Friends only user - friends only profile
        cls.user_friends_only.profile.privacy_settings.profile_visibility = 'friends_only'
        cls.user_friends_only.profile.privacy_settings.save()

        # Private user - private profile
        cls.user_private.profile.privacy_settings.profile_visibility = 'private'
        cls.user_private.profile.privacy_settings.save()

        # Add some profile data
        cls.user_public.profile.bio = "Public user bio"
        cls.user_public.profile.occupation = "engineer"
        cls.user_public.profile.country = "us"
        cls.user_public.profile.save()

        cls.user_friends_only.profile.bio = "Friends only bio"
        cls.user_friends_only.profile.occupation = "teacher"
        cls.user_friends_only.profile.save()

        cls.user_private.profile.bio = "Private user bio"
        cls.user_private.profile.occupation = "doctor"
        cls.user_private.profile.save()

    def setUp(self):
        """Set up test environment for each test method."""
        self.factory = APIRequestFactory()

    def _get_serializer_with_user_context(self, target_profile, requesting_user=None):
        """Helper method to create serializer with proper context."""
        request = self.factory.get('/')

        # Create DRF request for URL generation
        drf_request = Request(request)

        # Build context
        context = {'request': drf_request}

        # For tests, pass the user directly in context
        if requesting_user:
            context['test_user'] = requesting_user

        return ProfileSerializer(target_profile, context=context)



    def test_user_viewing_own_profile_shows_all_fields(self):
        """Test that users can always see their own complete profile."""
        serializer = self._get_serializer_with_user_context(
            self.user_private.profile, self.user_private
        )
        data = serializer.data

        # User should see all their own profile data
        self.assertIn('bio', data)
        self.assertIn('occupation', data)
        self.assertIn('country', data)
        self.assertIn('user_url', data)
        self.assertEqual(data['bio'], 'Private user bio')
        self.assertEqual(data['occupation'], 'doctor')

    def test_admin_viewing_profile_shows_all_fields(self):
        """Test that admin users can see all profile data."""
        serializer = self._get_serializer_with_user_context(
            self.user_private.profile, self.admin_user
        )
        data = serializer.data

        # Admin should see all data regardless of privacy settings
        self.assertIn('bio', data)
        self.assertIn('occupation', data)
        self.assertIn('user_url', data)
        self.assertEqual(data['bio'], 'Private user bio')

    def test_public_profile_visibility(self):
        """Test that public profiles are visible to everyone."""
        # Stranger viewing public profile
        serializer = self._get_serializer_with_user_context(
            self.user_public.profile, self.user_stranger
        )
        data = serializer.data

        # Should see all profile data
        self.assertIn('bio', data)
        self.assertIn('occupation', data)
        self.assertIn('country', data)
        self.assertEqual(data['bio'], 'Public user bio')
        self.assertEqual(data['occupation'], 'engineer')

        # Anonymous user viewing public profile
        serializer = self._get_serializer_with_user_context(
            self.user_public.profile
        )
        data = serializer.data

        # Anonymous users should not see public profiles (need authentication)
        # Should only return limited fields
        self.assertEqual(len(data), 2)  # Only 'url' and 'user_url'
        self.assertIn('url', data)
        self.assertIn('user_url', data)

    def test_friends_only_profile_visibility(self):
        """Test that friends-only profiles are only visible to friends."""
        # Friend viewing friends-only profile
        serializer = self._get_serializer_with_user_context(
            self.user_friends_only.profile, self.user_friend
        )
        data = serializer.data

        # Friend should see all profile data
        self.assertIn('bio', data)
        self.assertIn('occupation', data)
        self.assertEqual(data['bio'], 'Friends only bio')
        self.assertEqual(data['occupation'], 'teacher')

        # Stranger viewing friends-only profile
        serializer = self._get_serializer_with_user_context(
            self.user_friends_only.profile, self.user_stranger
        )
        data = serializer.data

        # Stranger should only see limited fields
        self.assertEqual(len(data), 2)  # Only 'url' and 'user_url'
        self.assertIn('url', data)
        self.assertIn('user_url', data)
        self.assertNotIn('bio', data)
        self.assertNotIn('occupation', data)

    def test_profile_without_privacy_settings(self):
        """Test profile serialization when privacy settings are missing."""
        # Create user and delete privacy settings
        user_no_settings = User.objects.create_user(
            username="no_settings",
            email="no@example.com"
        )
        user_no_settings.profile.privacy_settings.delete()
        user_no_settings.profile.bio = "No settings bio"
        user_no_settings.profile.save()

        # Establish friendship (since default behavior is friends_only)
        user_no_settings.profile.friends.add(self.user_friend)
        self.user_friend.profile.friends.add(user_no_settings)

        # Friend viewing profile without privacy settings
        serializer = self._get_serializer_with_user_context(
            user_no_settings.profile, self.user_friend
        )
        data = serializer.data

        # Should default to friends_only behavior (friend can see it)
        self.assertIn('bio', data)
        self.assertEqual(data['bio'], 'No settings bio')

        # Stranger viewing profile without privacy settings
        serializer = self._get_serializer_with_user_context(
            user_no_settings.profile, self.user_stranger
        )
        data = serializer.data

        # Stranger should only see limited fields (default friends_only)
        self.assertEqual(len(data), 2)
        self.assertNotIn('bio', data)

    def test_private_profile_visibility(self):
        """Test that private profiles are only visible to the owner."""
        # Friend viewing private profile (should not see it)
        serializer = self._get_serializer_with_user_context(
            self.user_private.profile, self.user_friend
        )
        data = serializer.data

        # Even friends should only see limited fields for private profiles
        self.assertEqual(len(data), 2)  # Only 'url' and 'user_url'
        self.assertIn('url', data)
        self.assertIn('user_url', data)
        self.assertNotIn('bio', data)

        # Stranger viewing private profile
        serializer = self._get_serializer_with_user_context(
            self.user_private.profile, self.user_stranger
        )
        data = serializer.data

        # Should only see limited fields
        self.assertEqual(len(data), 2)
        self.assertNotIn('bio', data)
        self.assertNotIn('occupation', data)


    def test_anonymous_user_access_to_profiles(self):
        """Test that anonymous users can't see any profile details."""
        profiles_to_test = [
            self.user_public.profile,
            self.user_friends_only.profile,
            self.user_private.profile
        ]

        for profile in profiles_to_test:
            serializer = self._get_serializer_with_user_context(profile)
            data = serializer.data

            # Anonymous users should only see limited fields
            self.assertEqual(len(data), 2)
            self.assertIn('url', data)
            self.assertIn('user_url', data)
            self.assertNotIn('bio', data)
            self.assertNotIn('occupation', data)

    def test_profile_visibility_consistency(self):
        """Test that profile visibility is consistent across multiple requests."""
        # Serialize the same profile multiple times
        serializer1 = self._get_serializer_with_user_context(
            self.user_friends_only.profile, self.user_stranger
        )
        data1 = serializer1.data

        serializer2 = self._get_serializer_with_user_context(
            self.user_friends_only.profile, self.user_stranger
        )
        data2 = serializer2.data

        # Should be identical
        self.assertEqual(data1, data2)

    def test_profile_visibility_change_affects_serialization(self):
        """Test that changing profile visibility affects serialization."""
        # Initial serialization with friends_only
        serializer = self._get_serializer_with_user_context(
            self.user_friends_only.profile, self.user_stranger
        )
        data_private = serializer.data
        self.assertNotIn('bio', data_private)

        # Change to public visibility
        self.user_friends_only.profile.privacy_settings.profile_visibility = 'public'
        self.user_friends_only.profile.privacy_settings.save()

        # Serialize again
        serializer = self._get_serializer_with_user_context(
            self.user_friends_only.profile, self.user_stranger
        )
        data_public = serializer.data
        self.assertIn('bio', data_public)
        self.assertEqual(data_public['bio'], 'Friends only bio')

    def test_serializer_preserves_basic_fields_in_limited_view(self):
        """Test that limited view always includes basic identification fields."""
        serializer = self._get_serializer_with_user_context(
            self.user_private.profile, self.user_stranger
        )
        data = serializer.data

        # These fields should always be present even in limited view
        self.assertIn('url', data)
        self.assertIn('user_url', data)

        # These should be filtered out
        self.assertNotIn('bio', data)
        self.assertNotIn('occupation', data)
        self.assertNotIn('country', data)
        self.assertNotIn('preferred_language', data)
        self.assertNotIn('picture', data)
        self.assertNotIn('friends', data)

    def test_friends_list_visibility_in_profile(self):
        """Test that friends list is properly filtered based on profile visibility."""
        # Add some friends to test visibility
        extra_friend = User.objects.create_user(username="extra_friend", email="extra@example.com")
        self.user_public.profile.friends.add(extra_friend)

        # Public profile - stranger should see friends list
        serializer = self._get_serializer_with_user_context(
            self.user_public.profile, self.user_stranger
        )
        data = serializer.data
        self.assertIn('friends', data)

        # Private profile - stranger should not see friends list
        serializer = self._get_serializer_with_user_context(
            self.user_private.profile, self.user_stranger
        )
        data = serializer.data
        self.assertNotIn('friends', data)

    def test_profile_with_empty_privacy_settings(self):
        """Test profile behavior with default privacy settings values."""
        # Create user with default privacy settings
        user_default = User.objects.create_user(
            username="default_user",
            email="default@example.com"
        )
        user_default.profile.bio = "Default privacy bio"
        user_default.profile.save()

        # Check default privacy settings (should be friends_only)
        privacy_settings = user_default.profile.privacy_settings
        self.assertEqual(privacy_settings.profile_visibility, 'friends_only')

        # Stranger should not see the profile
        serializer = self._get_serializer_with_user_context(
            user_default.profile, self.user_stranger
        )
        data = serializer.data
        self.assertEqual(len(data), 2)  # Only basic fields
        self.assertNotIn('bio', data)
