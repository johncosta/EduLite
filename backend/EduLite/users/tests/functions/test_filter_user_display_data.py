# backend/EduLite/users/tests/functions/test_filter_user_display_data.py
# Tests for the filter_user_display_data function from user_search_logic.py

from django.test import TestCase
from django.contrib.auth import get_user_model

from users.logic.user_search_logic import filter_user_display_data
from users.models import UserProfile, UserProfilePrivacySettings

User = get_user_model()


class FilterUserDisplayDataTests(TestCase):
    """
    Test suite for the filter_user_display_data function.
    Tests data filtering for display purposes (future extensibility).
    """

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all test methods."""
        cls.user1 = User.objects.create_user(
            username="user1",
            first_name="First",
            last_name="User",
            email="user1@example.com"
        )

        cls.user2 = User.objects.create_user(
            username="user2",
            first_name="Second",
            last_name="User",
            email="user2@example.com"
        )

        cls.requesting_user = User.objects.create_user(
            username="requester",
            first_name="Requesting",
            last_name="User",
            email="requester@example.com"
        )

    def test_function_returns_same_queryset(self):
        """Test that function currently returns the same queryset (no filtering)."""
        base_queryset = User.objects.filter(
            username__in=["user1", "user2"]
        ).select_related('profile', 'profile__privacy_settings')

        filtered_queryset = filter_user_display_data(base_queryset, self.requesting_user)

        # Should return the same queryset for now
        self.assertEqual(list(base_queryset), list(filtered_queryset))

    def test_function_with_anonymous_user(self):
        """Test that function works with anonymous users."""
        base_queryset = User.objects.filter(
            username__in=["user1", "user2"]
        ).select_related('profile', 'profile__privacy_settings')

        filtered_queryset = filter_user_display_data(base_queryset, None)

        # Should return the same queryset
        self.assertEqual(list(base_queryset), list(filtered_queryset))

    def test_function_preserves_queryset_structure(self):
        """Test that function preserves queryset structure and annotations."""
        base_queryset = User.objects.filter(
            username__in=["user1", "user2"]
        ).select_related('profile', 'profile__privacy_settings').order_by('username')

        filtered_queryset = filter_user_display_data(base_queryset, self.requesting_user)

        # Should preserve ordering
        self.assertEqual(
            list(base_queryset.values_list('username', flat=True)),
            list(filtered_queryset.values_list('username', flat=True))
        )

    def test_function_with_empty_queryset(self):
        """Test that function handles empty querysets correctly."""
        empty_queryset = User.objects.none()

        filtered_queryset = filter_user_display_data(empty_queryset, self.requesting_user)

        # Should return empty queryset
        self.assertEqual(filtered_queryset.count(), 0)
        self.assertEqual(list(empty_queryset), list(filtered_queryset))

    def test_function_extensibility_hook(self):
        """Test that function serves as an extensibility hook for future features."""
        # This test documents the intended future functionality
        base_queryset = User.objects.filter(
            username__in=["user1", "user2"]
        ).select_related('profile', 'profile__privacy_settings')

        filtered_queryset = filter_user_display_data(base_queryset, self.requesting_user)

        # Currently should pass through unchanged
        # Future implementations might:
        # - Hide full names based on show_full_name setting
        # - Hide email addresses based on show_email setting
        # - Show different profile picture visibility levels
        self.assertIsNotNone(filtered_queryset)
        self.assertTrue(hasattr(filtered_queryset, 'count'))
