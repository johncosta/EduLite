# backend/EduLite/users/tests/functions/test_apply_privacy_filters.py
# Tests for the apply_privacy_filters function from user_search_logic.py

from django.test import TestCase
from django.contrib.auth import get_user_model

from users.logic.user_search_logic import apply_privacy_filters
from users.models import UserProfile, UserProfilePrivacySettings

User = get_user_model()


class ApplyPrivacyFiltersTests(TestCase):
    """
    Test suite for the apply_privacy_filters function.
    Tests privacy filtering logic for user search results.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all test methods."""
        # Create test users
        cls.user1 = User.objects.create_user(
            username="public_user",
            first_name="Public",
            last_name="User",
            email="public@example.com"
        )

        cls.user2 = User.objects.create_user(
            username="friends_only_user",
            first_name="Friends",
            last_name="Only",
            email="friends@example.com"
        )

        cls.user3 = User.objects.create_user(
            username="friends_of_friends_user",
            first_name="FriendsOf",
            last_name="Friends",
            email="fof@example.com"
        )

        cls.user4 = User.objects.create_user(
            username="nobody_user",
            first_name="Nobody",
            last_name="Private",
            email="private@example.com"
        )

        cls.requesting_user = User.objects.create_user(
            username="requester",
            first_name="Requesting",
            last_name="User",
            email="requester@example.com"
        )

        cls.mutual_friend = User.objects.create_user(
            username="mutual_friend",
            first_name="Mutual",
            last_name="Friend",
            email="mutual@example.com"
        )

        # Set up privacy settings
        cls.user1.profile.privacy_settings.search_visibility = 'everyone'
        cls.user1.profile.privacy_settings.save()

        cls.user2.profile.privacy_settings.search_visibility = 'friends_only'
        cls.user2.profile.privacy_settings.save()

        cls.user3.profile.privacy_settings.search_visibility = 'friends_of_friends'
        cls.user3.profile.privacy_settings.save()

        cls.user4.profile.privacy_settings.search_visibility = 'nobody'
        cls.user4.profile.privacy_settings.save()

        # Set up friendships
        # requesting_user is friends with user2 (friends_only_user)
        cls.requesting_user.profile.friends.add(cls.user2)
        cls.user2.profile.friends.add(cls.requesting_user)

        # mutual_friend is friends with requesting_user and user3
        cls.mutual_friend.profile.friends.add(cls.requesting_user)
        cls.requesting_user.profile.friends.add(cls.mutual_friend)
        cls.mutual_friend.profile.friends.add(cls.user3)
        cls.user3.profile.friends.add(cls.mutual_friend)


    def test_anonymous_user_sees_only_everyone_visibility(self):
        """Test that anonymous users only see users with 'everyone' visibility."""
        # Create a base queryset with all users
        base_queryset = User.objects.select_related('profile', 'profile__privacy_settings')

        filtered_queryset = apply_privacy_filters(base_queryset, None)
        usernames = list(filtered_queryset.values_list('username', flat=True))

        # Should only see public_user
        self.assertIn("public_user", usernames)
        self.assertNotIn("friends_only_user", usernames)
        self.assertNotIn("friends_of_friends_user", usernames)
        self.assertNotIn("nobody_user", usernames)

    def test_authenticated_user_sees_appropriate_users(self):
        """Test that authenticated users see users based on privacy settings."""
        base_queryset = User.objects.select_related('profile', 'profile__privacy_settings')

        filtered_queryset = apply_privacy_filters(base_queryset, self.requesting_user)
        usernames = list(filtered_queryset.values_list('username', flat=True))

        # Should see:
        # - public_user (everyone visibility)
        # - friends_only_user (direct friend)
        # - friends_of_friends_user (mutual friend through mutual_friend)
        # - requester (themselves)
        # Should NOT see:
        # - nobody_user (nobody visibility)
        self.assertIn("public_user", usernames)
        self.assertIn("friends_only_user", usernames)
        self.assertIn("friends_of_friends_user", usernames)
        self.assertIn("requester", usernames)
        self.assertNotIn("nobody_user", usernames)

    def test_user_can_always_find_themselves(self):
        """Test that users can always find themselves regardless of privacy settings."""
        # Set requester's privacy to 'nobody'
        self.requesting_user.profile.privacy_settings.search_visibility = 'nobody'
        self.requesting_user.profile.privacy_settings.save()

        base_queryset = User.objects.select_related('profile', 'profile__privacy_settings')
        filtered_queryset = apply_privacy_filters(base_queryset, self.requesting_user)
        usernames = list(filtered_queryset.values_list('username', flat=True))

        # Should still be able to find themselves
        self.assertIn("requester", usernames)

    def test_friends_only_visibility_blocks_non_friends(self):
        """Test that friends_only visibility blocks non-friends."""
        # Create a user who is not friends with friends_only_user
        non_friend = User.objects.create_user(
            username="non_friend",
            email="nonfriend@example.com"
        )

        base_queryset = User.objects.select_related('profile', 'profile__privacy_settings')
        filtered_queryset = apply_privacy_filters(base_queryset, non_friend)
        usernames = list(filtered_queryset.values_list('username', flat=True))

        # Should see public_user but not friends_only_user
        self.assertIn("public_user", usernames)
        self.assertNotIn("friends_only_user", usernames)

    def test_friends_of_friends_visibility_with_mutual_friends(self):
        """Test friends_of_friends visibility works with mutual friends."""
        # Create another user who shares mutual_friend with user3
        another_user = User.objects.create_user(
            username="another_user",
            email="another@example.com"
        )

        # Make another_user friends with mutual_friend
        another_user.profile.friends.add(self.mutual_friend)
        self.mutual_friend.profile.friends.add(another_user)

        base_queryset = User.objects.select_related('profile', 'profile__privacy_settings')
        filtered_queryset = apply_privacy_filters(base_queryset, another_user)
        usernames = list(filtered_queryset.values_list('username', flat=True))

        # Should see friends_of_friends_user through mutual_friend
        self.assertIn("friends_of_friends_user", usernames)

    def test_friends_of_friends_visibility_without_mutual_friends(self):
        """Test friends_of_friends visibility blocks users without mutual friends."""
        # Create a user with no mutual friends with user3
        isolated_user = User.objects.create_user(
            username="isolated_user",
            email="isolated@example.com"
        )

        base_queryset = User.objects.select_related('profile', 'profile__privacy_settings')
        filtered_queryset = apply_privacy_filters(base_queryset, isolated_user)
        usernames = list(filtered_queryset.values_list('username', flat=True))

        # Should NOT see friends_of_friends_user
        self.assertNotIn("friends_of_friends_user", usernames)
        # But should see public users
        self.assertIn("public_user", usernames)

    def test_nobody_visibility_blocks_everyone_except_self(self):
        """Test that nobody visibility blocks everyone except the user themselves."""
        base_queryset = User.objects.select_related('profile', 'profile__privacy_settings')

        # Test from nobody_user's perspective
        filtered_queryset = apply_privacy_filters(base_queryset, self.user4)  # nobody_user
        usernames = list(filtered_queryset.values_list('username', flat=True))

        # Should see themselves and public users, but not friends-only users
        self.assertIn("nobody_user", usernames)  # themselves
        self.assertIn("public_user", usernames)  # everyone visibility

        # Test from another user's perspective
        filtered_queryset = apply_privacy_filters(base_queryset, self.requesting_user)
        usernames = list(filtered_queryset.values_list('username', flat=True))

        # Should NOT see nobody_user
        self.assertNotIn("nobody_user", usernames)

    def test_direct_friends_override_friends_of_friends_logic(self):
        """Test that direct friendships work even with friends_of_friends setting."""
        # Make requesting_user directly friends with user3 (friends_of_friends_user)
        self.requesting_user.profile.friends.add(self.user3)
        self.user3.profile.friends.add(self.requesting_user)

        base_queryset = User.objects.select_related('profile', 'profile__privacy_settings')
        filtered_queryset = apply_privacy_filters(base_queryset, self.requesting_user)
        usernames = list(filtered_queryset.values_list('username', flat=True))

        # Should see friends_of_friends_user as a direct friend
        self.assertIn("friends_of_friends_user", usernames)

    def test_queryset_efficiency_with_select_related(self):
        """Test that the function maintains queryset efficiency."""
        base_queryset = User.objects.select_related('profile', 'profile__privacy_settings')
        filtered_queryset = apply_privacy_filters(base_queryset, self.requesting_user)

        # Should maintain select_related for efficiency
        query_str = str(filtered_queryset.query)
        self.assertIn("profile", query_str)

    def test_empty_queryset_returns_empty(self):
        """Test that an empty base queryset returns empty filtered queryset."""
        empty_queryset = User.objects.none()
        filtered_queryset = apply_privacy_filters(empty_queryset, self.requesting_user)

        self.assertEqual(filtered_queryset.count(), 0)
