# backend/EduLite/users/tests/serializers/test_privacy_aware_user_serializer.py
# Tests for privacy-aware UserSerializer functionality

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request

from users.serializers import UserSerializer
from users.models import UserProfile, UserProfilePrivacySettings

User = get_user_model()


class PrivacyAwareUserSerializerTests(TestCase):
    """
    Test suite for privacy-aware UserSerializer functionality.
    Tests field visibility based on privacy settings and user relationships.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all test methods."""
        # Create users
        cls.user_public = User.objects.create_user(
            username="public_user",
            first_name="Public",
            last_name="User",
            email="public@example.com"
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
        cls.user_private.profile.friends.add(cls.user_friend)
        cls.user_friend.profile.friends.add(cls.user_private)

        # Configure privacy settings
        # Public user - shows everything
        cls.user_public.profile.privacy_settings.show_full_name = True
        cls.user_public.profile.privacy_settings.show_email = True
        cls.user_public.profile.privacy_settings.save()

        # Private user - hides everything
        cls.user_private.profile.privacy_settings.show_full_name = False
        cls.user_private.profile.privacy_settings.show_email = False
        cls.user_private.profile.privacy_settings.save()

        # Friend user - shows name but not email
        cls.user_friend.profile.privacy_settings.show_full_name = True
        cls.user_friend.profile.privacy_settings.show_email = False
        cls.user_friend.profile.privacy_settings.save()

        # Stranger user - default settings
        cls.user_stranger.profile.privacy_settings.show_full_name = True
        cls.user_stranger.profile.privacy_settings.show_email = False
        cls.user_stranger.profile.privacy_settings.save()

    def setUp(self):
        """Set up test environment for each test method."""
        self.factory = APIRequestFactory()

    # In test_privacy_aware_user_serializer.py
    def _get_serializer_with_user_context(self, target_user, requesting_user=None):
        """Helper method to create serializer with proper context."""
        request = self.factory.get('/')
        drf_request = Request(request)

        context = {'request': drf_request}

        # For tests, pass the user directly in context
        if requesting_user:
            context['test_user'] = requesting_user

        return UserSerializer(target_user, context=context)


    def test_user_viewing_own_profile_shows_all_fields(self):
        """Test that users can always see their own complete profile data."""
        serializer = self._get_serializer_with_user_context(
            self.user_private, self.user_private
        )
        data = serializer.data

        # User should see all their own data regardless of privacy settings
        self.assertIn('email', data)
        self.assertIn('first_name', data)
        self.assertIn('last_name', data)
        self.assertIn('full_name', data)
        self.assertEqual(data['email'], 'private@example.com')
        self.assertEqual(data['first_name'], 'Private')
        self.assertEqual(data['last_name'], 'User')
        self.assertEqual(data['full_name'], 'Private User')

    def test_admin_viewing_profile_shows_all_fields(self):
        """Test that admin users can see all profile data."""
        serializer = self._get_serializer_with_user_context(
            self.user_private, self.admin_user
        )
        data = serializer.data

        # Admin should see all data regardless of privacy settings
        self.assertIn('email', data)
        self.assertIn('first_name', data)
        self.assertIn('last_name', data)
        self.assertIn('full_name', data)
        self.assertEqual(data['email'], 'private@example.com')
        self.assertEqual(data['first_name'], 'Private')

    def test_public_user_privacy_settings(self):
        """Test serialization of user with public privacy settings."""
        serializer = self._get_serializer_with_user_context(
            self.user_public, self.user_stranger
        )
        data = serializer.data

        # Public user shows everything
        self.assertIn('email', data)
        self.assertIn('first_name', data)
        self.assertIn('last_name', data)
        self.assertIn('full_name', data)
        self.assertEqual(data['email'], 'public@example.com')
        self.assertEqual(data['first_name'], 'Public')

    def test_private_user_privacy_settings(self):
        """Test serialization of user with private privacy settings."""
        serializer = self._get_serializer_with_user_context(
            self.user_private, self.user_stranger
        )
        data = serializer.data

        # Private user hides name and email
        self.assertNotIn('email', data)
        self.assertNotIn('first_name', data)
        self.assertNotIn('last_name', data)
        self.assertNotIn('full_name', data)

        # But still shows basic info
        self.assertIn('username', data)
        self.assertIn('url', data)
        self.assertEqual(data['username'], 'private_user')

    def test_mixed_privacy_settings(self):
        """Test user with show_full_name=True but show_email=False."""
        serializer = self._get_serializer_with_user_context(
            self.user_friend, self.user_stranger
        )
        data = serializer.data

        # Should show name but not email
        self.assertNotIn('email', data)
        self.assertIn('first_name', data)
        self.assertIn('last_name', data)
        self.assertIn('full_name', data)
        self.assertEqual(data['first_name'], 'Friend')
        self.assertEqual(data['full_name'], 'Friend User')

    def test_anonymous_user_context(self):
        """Test serialization without authentication context."""
        serializer = self._get_serializer_with_user_context(self.user_public)
        data = serializer.data

        # Without authentication, should respect privacy settings
        # Public user with show_email=True should still show email to anonymous
        self.assertIn('email', data)
        self.assertIn('first_name', data)

        # Test private user
        serializer = self._get_serializer_with_user_context(self.user_private)
        data = serializer.data

        # Private user should hide info even from anonymous users
        self.assertNotIn('email', data)
        self.assertNotIn('first_name', data)

    def test_user_without_privacy_settings(self):
        """Test serialization of user without privacy settings."""
        # Create user without privacy settings
        user_no_settings = User.objects.create_user(
            username="no_settings",
            first_name="No",
            last_name="Settings",
            email="no@example.com"
        )

        # Delete the auto-created privacy settings
        user_no_settings.profile.privacy_settings.delete()

        serializer = self._get_serializer_with_user_context(
            user_no_settings, self.user_stranger
        )
        data = serializer.data

        # Should default to conservative privacy (show name, hide email)
        self.assertNotIn('email', data)  # Default to hiding email
        self.assertIn('first_name', data)  # Default to showing name
        self.assertEqual(data['first_name'], 'No')

    def test_serializer_preserves_non_privacy_fields(self):
        """Test that privacy filtering doesn't affect non-privacy fields."""
        serializer = self._get_serializer_with_user_context(
            self.user_private, self.user_stranger
        )
        data = serializer.data

        # These fields should always be present
        self.assertIn('id', data)
        self.assertIn('username', data)
        self.assertIn('url', data)
        self.assertIn('profile_url', data)
        self.assertIn('groups', data)

        # Verify correct values
        self.assertEqual(data['username'], 'private_user')
        self.assertEqual(data['id'], self.user_private.id)

    def test_full_name_method_respects_privacy(self):
        """Test that get_full_name method is properly filtered."""
        # User with visible name
        serializer = self._get_serializer_with_user_context(
            self.user_public, self.user_stranger
        )
        data = serializer.data
        self.assertEqual(data['full_name'], 'Public User')

        # User with hidden name
        serializer = self._get_serializer_with_user_context(
            self.user_private, self.user_stranger
        )
        data = serializer.data
        self.assertNotIn('full_name', data)

    def test_consistency_across_multiple_serializations(self):
        """Test that the same user gets consistent serialization."""
        # Serialize the same user multiple times
        serializer1 = self._get_serializer_with_user_context(
            self.user_private, self.user_stranger
        )
        data1 = serializer1.data

        serializer2 = self._get_serializer_with_user_context(
            self.user_private, self.user_stranger
        )
        data2 = serializer2.data

        # Should be identical
        self.assertEqual(data1, data2)

    def test_different_requesting_users_get_appropriate_data(self):
        """Test that different requesting users see appropriate data levels."""
        target_user = self.user_friend  # Shows name, hides email

        # Friend viewing - should see name, not email
        friend_serializer = self._get_serializer_with_user_context(
            target_user, self.user_private
        )
        friend_data = friend_serializer.data

        # Stranger viewing - should see name, not email
        stranger_serializer = self._get_serializer_with_user_context(
            target_user, self.user_stranger
        )
        stranger_data = stranger_serializer.data

        # Both should see same data since privacy settings are consistent
        self.assertEqual(friend_data.get('first_name'), 'Friend')
        self.assertEqual(stranger_data.get('first_name'), 'Friend')
        self.assertNotIn('email', friend_data)
        self.assertNotIn('email', stranger_data)

    def test_privacy_settings_change_affects_serialization(self):
        """Test that changing privacy settings affects serialization output."""
        # Initial serialization with private settings
        serializer = self._get_serializer_with_user_context(
            self.user_private, self.user_stranger
        )
        data_private = serializer.data
        self.assertNotIn('first_name', data_private)

        # Change privacy settings to public
        self.user_private.profile.privacy_settings.show_full_name = True
        self.user_private.profile.privacy_settings.save()

        # Serialize again
        serializer = self._get_serializer_with_user_context(
            self.user_private, self.user_stranger
        )
        data_public = serializer.data
        self.assertIn('first_name', data_public)
        self.assertEqual(data_public['first_name'], 'Private')
