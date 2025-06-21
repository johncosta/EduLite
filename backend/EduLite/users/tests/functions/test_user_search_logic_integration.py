# backend/EduLite/users/tests/functions/test_user_search_logic_integration.py
# Integration tests for user search logic with privacy controls

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory

from users.logic.user_search_logic import execute_user_search
from users.models import UserProfile, UserProfilePrivacySettings
from users.views import UserSearchView

User = get_user_model()


class UserSearchLogicIntegrationTests(TestCase):
    """
    Integration test suite for user search logic.
    Tests the complete user search workflow with privacy controls.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all test methods."""
        cls.searching_user = User.objects.create_user(
            username="searcher",
            first_name="Search",
            last_name="User",
            email="searcher@example.com"
        )

        # Set up request factory and view instance
        cls.factory = APIRequestFactory()
        cls.view = UserSearchView()

    def test_privacy_settings_edge_cases(self):
        """Test edge cases in privacy settings."""
        # Create a user who changes their privacy settings
        changing_user = User.objects.create_user(
            username="changing_user",
            first_name="Changing",
            last_name="User",
            email="changing@example.com"
        )

        # Initially set to 'everyone'
        changing_user.profile.privacy_settings.search_visibility = 'everyone'
        changing_user.profile.privacy_settings.save()

        request = self.factory.get('/search/')
        request.user = self.searching_user

        # Should find the user
        success, queryset, page_data, error_response = execute_user_search(
            search_query="changing",
            requesting_user=self.searching_user,
            request=request,
            view_instance=self.view,
            min_query_length=2,
            page_size=10
        )

        usernames = list(queryset.values_list('username', flat=True))
        self.assertIn("changing_user", usernames)

        # Change to 'nobody'
        changing_user.profile.privacy_settings.search_visibility = 'nobody'
        changing_user.profile.privacy_settings.save()

        # Should no longer find the user
        success, queryset, page_data, error_response = execute_user_search(
            search_query="changing",
            requesting_user=self.searching_user,
            request=request,
            view_instance=self.view,
            min_query_length=2,
            page_size=10
        )

        usernames = list(queryset.values_list('username', flat=True))
        self.assertNotIn("changing_user", usernames)

    def test_performance_with_large_friend_networks(self):
        """Test that the search functions perform well with large friend networks."""
        # This test ensures the implementation is efficient
        request = self.factory.get('/search/')
        request.user = self.searching_user

        # Execute search and measure basic functionality
        success, queryset, page_data, error_response = execute_user_search(
            search_query="user",
            requesting_user=self.searching_user,
            request=request,
            view_instance=self.view,
            min_query_length=2,
            page_size=10
        )

        # Should complete successfully regardless of network size
        self.assertTrue(success)
        self.assertIsNotNone(queryset)
        self.assertIsNone(error_response)

    def test_error_handling_in_pipeline(self):
        """Test error handling throughout the search pipeline."""
        request = self.factory.get('/search/')
        request.user = self.searching_user

        # Test with invalid query
        success, queryset, page_data, error_response = execute_user_search(
            search_query="x",  # Too short
            requesting_user=self.searching_user,
            request=request,
            view_instance=self.view,
            min_query_length=2,
            page_size=10
        )

        self.assertFalse(success)
        self.assertIsNone(queryset)
        self.assertIsNotNone(error_response)
        self.assertEqual(error_response.status_code, 400)
