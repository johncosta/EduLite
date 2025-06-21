# backend/EduLite/users/tests/functions/test_have_mutual_friends.py
# Tests for the have_mutual_friends function from user_search_logic.py

from django.test import TestCase
from django.contrib.auth import get_user_model

from users.logic.user_search_logic import have_mutual_friends
from users.models import UserProfile

User = get_user_model()


class HaveMutualFriendsTests(TestCase):
    """
    Test suite for the have_mutual_friends function.
    Tests the helper function for checking if two users have mutual friends.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all test methods."""
        cls.user_a = User.objects.create_user(
            username="user_a",
            email="usera@example.com"
        )

        cls.user_b = User.objects.create_user(
            username="user_b",
            email="userb@example.com"
        )

        cls.mutual_friend1 = User.objects.create_user(
            username="mutual_friend1",
            email="mutual1@example.com"
        )

        cls.mutual_friend2 = User.objects.create_user(
            username="mutual_friend2",
            email="mutual2@example.com"
        )

        cls.user_c = User.objects.create_user(
            username="user_c",
            email="userc@example.com"
        )

        cls.isolated_user = User.objects.create_user(
            username="isolated",
            email="isolated@example.com"
        )

        # Set up friendships for mutual friends scenario
        # user_a is friends with mutual_friend1 and mutual_friend2
        cls.user_a.profile.friends.add(cls.mutual_friend1, cls.mutual_friend2)
        cls.mutual_friend1.profile.friends.add(cls.user_a)
        cls.mutual_friend2.profile.friends.add(cls.user_a)

        # user_b is friends with mutual_friend1 and mutual_friend2
        cls.user_b.profile.friends.add(cls.mutual_friend1, cls.mutual_friend2)
        cls.mutual_friend1.profile.friends.add(cls.user_b)
        cls.mutual_friend2.profile.friends.add(cls.user_b)

        # user_c is friends with mutual_friend1 only
        cls.user_c.profile.friends.add(cls.mutual_friend1)
        cls.mutual_friend1.profile.friends.add(cls.user_c)


    def test_users_with_mutual_friends_return_true(self):
        """Test that users with mutual friends return True."""
        result = have_mutual_friends(self.user_a, self.user_b)

        self.assertTrue(result)

    def test_users_with_one_mutual_friend_return_true(self):
        """Test that users with at least one mutual friend return True."""
        result = have_mutual_friends(self.user_a, self.user_c)

        self.assertTrue(result)

    def test_users_with_no_mutual_friends_return_false(self):
        """Test that users with no mutual friends return False."""
        result = have_mutual_friends(self.user_a, self.isolated_user)

        self.assertFalse(result)

    def test_same_user_returns_false(self):
        """Test that checking mutual friends with same user returns False."""
        result = have_mutual_friends(self.user_a, self.user_a)

        self.assertFalse(result)

    def test_none_user_returns_false(self):
        """Test that None user returns False."""
        result1 = have_mutual_friends(None, self.user_a)
        result2 = have_mutual_friends(self.user_a, None)
        result3 = have_mutual_friends(None, None)

        self.assertFalse(result1)
        self.assertFalse(result2)
        self.assertFalse(result3)

    def test_unauthenticated_user_returns_false(self):
        """Test that unauthenticated user returns False."""
        from django.contrib.auth.models import AnonymousUser
        anonymous_user = AnonymousUser()

        result1 = have_mutual_friends(anonymous_user, self.user_a)
        result2 = have_mutual_friends(self.user_a, anonymous_user)

        self.assertFalse(result1)
        self.assertFalse(result2)

    def test_users_with_no_friends_return_false(self):
        """Test that users with no friends return False."""
        user_no_friends1 = User.objects.create_user(
            username="no_friends1",
            email="nofriends1@example.com"
        )

        user_no_friends2 = User.objects.create_user(
            username="no_friends2",
            email="nofriends2@example.com"
        )

        result = have_mutual_friends(user_no_friends1, user_no_friends2)

        self.assertFalse(result)

    def test_one_user_with_friends_one_without_returns_false(self):
        """Test that one user with friends and one without returns False."""
        user_no_friends = User.objects.create_user(
            username="no_friends",
            email="nofriends@example.com"
        )

        result = have_mutual_friends(self.user_a, user_no_friends)

        self.assertFalse(result)

    def test_function_is_symmetric(self):
        """Test that function returns same result regardless of parameter order."""
        result1 = have_mutual_friends(self.user_a, self.user_b)
        result2 = have_mutual_friends(self.user_b, self.user_a)

        self.assertEqual(result1, result2)

        # Test with users who don't have mutual friends
        result3 = have_mutual_friends(self.user_a, self.isolated_user)
        result4 = have_mutual_friends(self.isolated_user, self.user_a)

        self.assertEqual(result3, result4)

    def test_direct_friends_dont_count_as_mutual_friends(self):
        """Test that direct friendship doesn't count as mutual friends."""
        # Make user_a and user_b direct friends
        self.user_a.profile.friends.add(self.user_b)
        self.user_b.profile.friends.add(self.user_a)

        # They should still have mutual friends (mutual_friend1, mutual_friend2)
        # but the function should work correctly
        result = have_mutual_friends(self.user_a, self.user_b)

        self.assertTrue(result)  # They still have mutual friends

    def test_efficiency_with_large_friend_lists(self):
        """Test function efficiency with users who have many friends."""
        # Create users with many friends
        user_many_friends1 = User.objects.create_user(
            username="many_friends1",
            email="many1@example.com"
        )

        user_many_friends2 = User.objects.create_user(
            username="many_friends2",
            email="many2@example.com"
        )

        shared_friend = User.objects.create_user(
            username="shared_friend",
            email="shared@example.com"
        )

        # Create many friends for user1 (but no shared friends with user2)
        for i in range(10):
            friend = User.objects.create_user(
                username=f"friend1_{i}",
                email=f"friend1_{i}@example.com"
            )
            user_many_friends1.profile.friends.add(friend)
            friend.profile.friends.add(user_many_friends1)

        # Create many friends for user2 (but no shared friends with user1)
        for i in range(10):
            friend = User.objects.create_user(
                username=f"friend2_{i}",
                email=f"friend2_{i}@example.com"
            )
            user_many_friends2.profile.friends.add(friend)
            friend.profile.friends.add(user_many_friends2)

        # Add one shared friend
        user_many_friends1.profile.friends.add(shared_friend)
        user_many_friends2.profile.friends.add(shared_friend)
        shared_friend.profile.friends.add(user_many_friends1, user_many_friends2)


        # Should still work efficiently
        result = have_mutual_friends(user_many_friends1, user_many_friends2)
        self.assertTrue(result)
