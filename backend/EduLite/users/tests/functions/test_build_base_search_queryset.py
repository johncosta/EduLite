# backend/EduLite/users/tests/functions/test_build_base_search_queryset.py
# Tests for the build_base_search_queryset function from user_search_logic.py

from django.test import TestCase
from django.contrib.auth import get_user_model

from users.logic.user_search_logic import build_base_search_queryset
from users.models import UserProfile, UserProfilePrivacySettings

User = get_user_model()


class BuildBaseSearchQuerysetTests(TestCase):
    """
    Test suite for the build_base_search_queryset function.
    Tests the base search functionality without privacy filtering.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all test methods."""
        # Create test users with different name patterns
        cls.user1 = User.objects.create_user(
            username="john_doe",
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )

        cls.user2 = User.objects.create_user(
            username="jane_smith",
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com"
        )

        cls.user3 = User.objects.create_user(
            username="johnsmith",
            first_name="Johnny",
            last_name="Johnson",
            email="johnny@example.com"
        )

        cls.user4 = User.objects.create_user(
            username="alice_wonderland",
            first_name="Alice",
            last_name="Wonderland",
            email="alice@example.com"
        )

        # User with no first/last name
        cls.user5 = User.objects.create_user(
            username="noname",
            email="noname@example.com"
        )

    def test_search_by_username(self):
        """Test searching by username returns correct results."""
        queryset = build_base_search_queryset("john")
        usernames = list(queryset.values_list('username', flat=True))

        # Should find john_doe and johnsmith
        self.assertIn("john_doe", usernames)
        self.assertIn("johnsmith", usernames)
        self.assertNotIn("jane_smith", usernames)
        self.assertNotIn("alice_wonderland", usernames)

    def test_search_by_first_name(self):
        """Test searching by first name returns correct results."""
        # Use "Johnny" which should only match the first_name of johnsmith user
        queryset = build_base_search_queryset("Johnny")
        usernames = list(queryset.values_list('username', flat=True))

        # Should find johnsmith (first_name="Johnny")
        self.assertIn("johnsmith", usernames)
        # Should not find other users
        self.assertNotIn("john_doe", usernames)
        self.assertNotIn("jane_smith", usernames)
        self.assertNotIn("alice_wonderland", usernames)


    def test_search_by_last_name(self):
        """Test searching by last name returns correct results."""
        queryset = build_base_search_queryset("Smith")
        usernames = list(queryset.values_list('username', flat=True))

        # Should find jane_smith
        self.assertIn("jane_smith", usernames)
        self.assertNotIn("john_doe", usernames)

    def test_case_insensitive_search(self):
        """Test that search is case insensitive."""
        queryset_lower = build_base_search_queryset("john")
        queryset_upper = build_base_search_queryset("JOHN")
        queryset_mixed = build_base_search_queryset("JoHn")

        # All should return the same results
        usernames_lower = set(queryset_lower.values_list('username', flat=True))
        usernames_upper = set(queryset_upper.values_list('username', flat=True))
        usernames_mixed = set(queryset_mixed.values_list('username', flat=True))

        self.assertEqual(usernames_lower, usernames_upper)
        self.assertEqual(usernames_lower, usernames_mixed)

    def test_partial_match_search(self):
        """Test that partial matches work correctly."""
        queryset = build_base_search_queryset("Jo")
        usernames = list(queryset.values_list('username', flat=True))

        # Should find users with "Jo" in username, first_name, or last_name
        expected_users = ["john_doe", "johnsmith"]  # Both have "Jo" in names
        for expected_user in expected_users:
            self.assertIn(expected_user, usernames)

    def test_search_with_whitespace(self):
        """Test that search query with whitespace is handled correctly."""
        queryset = build_base_search_queryset("  john  ")
        usernames = list(queryset.values_list('username', flat=True))

        # Should still find john-related users
        self.assertIn("john_doe", usernames)
        self.assertIn("johnsmith", usernames)

    def test_no_matches_returns_empty_queryset(self):
        """Test that search with no matches returns empty queryset."""
        queryset = build_base_search_queryset("nonexistentuser")

        self.assertEqual(queryset.count(), 0)

    def test_queryset_is_ordered_by_username(self):
        """Test that returned queryset is ordered by username."""
        queryset = build_base_search_queryset("a")  # Should match alice_wonderland

        # Check that queryset has order_by applied
        self.assertIn("username", str(queryset.query.order_by))

    def test_queryset_has_related_objects_selected(self):
        """Test that queryset has profile and privacy_settings selected for efficiency."""
        queryset = build_base_search_queryset("john")

        # Check that select_related is applied
        query_str = str(queryset.query)
        self.assertIn("profile", query_str)

    def test_distinct_results(self):
        """Test that results are distinct (no duplicates)."""
        # Create a user that might match on multiple fields
        user_duplicate_match = User.objects.create_user(
            username="test_user",
            first_name="test",
            last_name="user",
            email="test@example.com"
        )

        queryset = build_base_search_queryset("test")
        usernames = list(queryset.values_list('username', flat=True))

        # Should only appear once even though it matches on multiple fields
        username_count = usernames.count("test_user")
        self.assertEqual(username_count, 1)

    def test_empty_names_dont_cause_errors(self):
        """Test that users with empty first/last names don't cause errors."""
        queryset = build_base_search_queryset("noname")
        usernames = list(queryset.values_list('username', flat=True))

        # Should find the user with username "noname"
        self.assertIn("noname", usernames)
