# backend/EduLite/users/tests/functions/test_get_user_friends_ids.py
# Tests for the get_user_friends_ids function from user_search_logic.py

from django.test import TestCase
from django.contrib.auth import get_user_model

from users.logic.user_search_logic import get_user_friends_ids
from users.models import UserProfile

User = get_user_model()


class GetUserFriendsIdsTests(TestCase):
    """
    Test suite for the get_user_friends_ids function.
    Tests the helper function for efficiently getting user's friend IDs.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all test methods."""
        cls.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com"
        )

        cls.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com"
        )

        cls.user3 = User.objects.create_user(
            username="user3",
            email="user3@example.com"
        )

        cls.user4 = User.objects.create_user(
            username="user4",
            email="user4@example.com"
        )

        cls.user_with_no_friends = User.objects.create_user(
            username="loner",
            email="loner@example.com"
        )

        # Set up friendships
        # user1 is friends with user2 and user3
        cls.user1.profile.friends.add(cls.user2, cls.user3)
        cls.user2.profile.friends.add(cls.user1)
        cls.user3.profile.friends.add(cls.user1)

        # user2 is also friends with user4
        cls.user2.profile.friends.add(cls.user4)
        cls.user4.profile.friends.add(cls.user2)

    def test_get_friends_ids_for_user_with_friends(self):
        """Test getting friend IDs for a user who has friends."""
        friend_ids = get_user_friends_ids(self.user1)

        expected_ids = {self.user2.id, self.user3.id}
        self.assertEqual(friend_ids, expected_ids)
        self.assertIsInstance(friend_ids, set)

    def test_get_friends_ids_for_user_with_no_friends(self):
        """Test getting friend IDs for a user who has no friends."""
        friend_ids = get_user_friends_ids(self.user_with_no_friends)

        self.assertEqual(friend_ids, set())
        self.assertIsInstance(friend_ids, set)

    def test_get_friends_ids_for_none_user(self):
        """Test getting friend IDs for None user."""
        friend_ids = get_user_friends_ids(None)

        self.assertEqual(friend_ids, set())
        self.assertIsInstance(friend_ids, set)

    def test_get_friends_ids_for_unauthenticated_user(self):
        """Test getting friend IDs for unauthenticated user."""
        from django.contrib.auth.models import AnonymousUser
        anonymous_user = AnonymousUser()

        friend_ids = get_user_friends_ids(anonymous_user)

        self.assertEqual(friend_ids, set())
        self.assertIsInstance(friend_ids, set)

    def test_get_friends_ids_different_users_different_results(self):
        """Test that different users return different friend sets."""
        user1_friends = get_user_friends_ids(self.user1)
        user2_friends = get_user_friends_ids(self.user2)

        # user1 friends: {user2, user3}
        # user2 friends: {user1, user4}
        self.assertNotEqual(user1_friends, user2_friends)

        # They should share user1 and user2 but in different roles
        self.assertIn(self.user2.id, user1_friends)
        self.assertIn(self.user1.id, user2_friends)

    def test_get_friends_ids_returns_set_type(self):
        """Test that function always returns a set type."""
        # Test with user who has friends
        friend_ids_with_friends = get_user_friends_ids(self.user1)
        self.assertIsInstance(friend_ids_with_friends, set)

        # Test with user who has no friends
        friend_ids_no_friends = get_user_friends_ids(self.user_with_no_friends)
        self.assertIsInstance(friend_ids_no_friends, set)

        # Test with None
        friend_ids_none = get_user_friends_ids(None)
        self.assertIsInstance(friend_ids_none, set)

    def test_get_friends_ids_efficiency_single_query(self):
        """Test that function is efficient and doesn't cause N+1 queries."""
        # This test ensures the function uses values_list efficiently
        with self.assertNumQueries(1):  # Should be a single query
            friend_ids = get_user_friends_ids(self.user1)
            # Convert to list to force query execution
            list(friend_ids)

    def test_get_friends_ids_with_user_without_profile(self):
        """Test getting friend IDs for user who might not have a profile."""
        # Create a user without going through normal creation process
        user_without_profile = User.objects.create(
            username="no_profile",
            email="noprofile@example.com"
        )

        # Remove profile if it was created by signals
        if hasattr(user_without_profile, 'profile'):
            user_without_profile.profile.delete()

        friend_ids = get_user_friends_ids(user_without_profile)

        # Should handle gracefully and return empty set
        self.assertEqual(friend_ids, set())
        self.assertIsInstance(friend_ids, set)

    def test_get_friends_ids_contains_correct_types(self):
        """Test that returned set contains integer IDs."""
        friend_ids = get_user_friends_ids(self.user1)

        for friend_id in friend_ids:
            self.assertIsInstance(friend_id, int)
            self.assertGreater(friend_id, 0)
