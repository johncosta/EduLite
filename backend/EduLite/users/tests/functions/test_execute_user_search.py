# backend/EduLite/users/tests/functions/test_execute_user_search.py
# Tests for the execute_user_search function from user_search_logic.py

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory

from users.logic.user_search_logic import execute_user_search
from users.models import UserProfile, UserProfilePrivacySettings
from users.views import UserSearchView

User = get_user_model()


class ExecuteUserSearchTests(TestCase):
    """
    Test suite for the execute_user_search function.
    Tests the main orchestration function for user search with privacy controls.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all test methods."""
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
            username="private_user",
            first_name="Private",
            last_name="User",
            email="private@example.com"
        )

        cls.requesting_user = User.objects.create_user(
            username="requester",
            first_name="Requesting",
            last_name="User",
            email="requester@example.com"
        )

        # Set up privacy settings
        cls.user1.profile.privacy_settings.search_visibility = 'everyone'
        cls.user1.profile.privacy_settings.save()

        cls.user2.profile.privacy_settings.search_visibility = 'everyone'
        cls.user2.profile.privacy_settings.save()

        cls.user3.profile.privacy_settings.search_visibility = 'nobody'
        cls.user3.profile.privacy_settings.save()

        # Set up request factory and view instance
        cls.factory = APIRequestFactory()
        cls.view = UserSearchView()

    def create_mock_request(self, user=None):
        """Helper method to create a mock request."""
        request = self.factory.get('/search/')
        if user:
            request.user = user
        else:
            from django.contrib.auth.models import AnonymousUser
            request.user = AnonymousUser()
        return request

    def test_successful_search_with_results(self):
        """Test successful search that returns results."""
        request = self.create_mock_request(self.requesting_user)

        success, queryset, page_data, error_response = execute_user_search(
            search_query="john",
            requesting_user=self.requesting_user,
            request=request,
            view_instance=self.view,
            min_query_length=2,
            page_size=10
        )

        self.assertTrue(success)
        self.assertIsNotNone(queryset)
        self.assertIsNone(error_response)

        # Should find john_doe
        usernames = list(queryset.values_list('username', flat=True))
        self.assertIn("john_doe", usernames)

    def test_search_with_invalid_query_returns_error(self):
        """Test that invalid search query returns error response."""
        request = self.create_mock_request(self.requesting_user)

        success, queryset, page_data, error_response = execute_user_search(
            search_query="a",  # Too short
            requesting_user=self.requesting_user,
            request=request,
            view_instance=self.view,
            min_query_length=2,
            page_size=10
        )

        self.assertFalse(success)
        self.assertIsNone(queryset)
        self.assertIsNone(page_data)
        self.assertIsNotNone(error_response)
        self.assertEqual(error_response.status_code, 400)

    def test_search_with_empty_query_returns_error(self):
        """Test that empty search query returns error response."""
        request = self.create_mock_request(self.requesting_user)

        success, queryset, page_data, error_response = execute_user_search(
            search_query="",
            requesting_user=self.requesting_user,
            request=request,
            view_instance=self.view,
            min_query_length=2,
            page_size=10
        )

        self.assertFalse(success)
        self.assertIsNone(queryset)
        self.assertIsNone(page_data)
        self.assertIsNotNone(error_response)

    def test_search_respects_privacy_settings(self):
        """Test that search respects user privacy settings."""
        request = self.create_mock_request(self.requesting_user)

        success, queryset, page_data, error_response = execute_user_search(
            search_query="user",  # Should match both private_user and requesting user
            requesting_user=self.requesting_user,
            request=request,
            view_instance=self.view,
            min_query_length=2,
            page_size=10
        )

        self.assertTrue(success)
        self.assertIsNotNone(queryset)
        self.assertIsNone(error_response)

        usernames = list(queryset.values_list('username', flat=True))

        # Should find themselves but not private_user (privacy set to 'nobody')
        self.assertIn("requester", usernames)
        self.assertNotIn("private_user", usernames)

    def test_search_with_anonymous_user(self):
        """Test search functionality with anonymous user."""
        request = self.create_mock_request(None)  # Anonymous user

        success, queryset, page_data, error_response = execute_user_search(
            search_query="john",
            requesting_user=None,
            request=request,
            view_instance=self.view,
            min_query_length=2,
            page_size=10
        )

        self.assertTrue(success)
        self.assertIsNotNone(queryset)
        self.assertIsNone(error_response)

        usernames = list(queryset.values_list('username', flat=True))

        # Anonymous users should only see 'everyone' visibility users
        self.assertIn("john_doe", usernames)  # everyone visibility
        self.assertNotIn("private_user", usernames)  # nobody visibility

    def test_search_with_custom_min_length(self):
        """Test search with custom minimum query length."""
        request = self.create_mock_request(self.requesting_user)

        success, queryset, page_data, error_response = execute_user_search(
            search_query="ab",  # 2 characters
            requesting_user=self.requesting_user,
            request=request,
            view_instance=self.view,
            min_query_length=3,  # Require 3 characters
            page_size=10
        )

        self.assertFalse(success)
        self.assertIsNone(queryset)
        self.assertIsNotNone(error_response)

    def test_search_with_custom_page_size(self):
        """Test search with custom page size."""
        # Create more users to test pagination
        for i in range(15):
            User.objects.create_user(
                username=f"testuser{i}",
                first_name="Test",
                last_name=f"User{i}",
                email=f"test{i}@example.com"
            )

        request = self.create_mock_request(self.requesting_user)

        success, queryset, paginator, error_response = execute_user_search(
            search_query="test",
            requesting_user=self.user1,
            request=request,
            view_instance=self.mock_view,
            page_size=5
        )

        self.assertTrue(success)
        self.assertIsNone(error_response)
        if paginator is not None:
            # Check the page size on the paginator
            self.assertEqual(paginator.page_size, 5)
            # Check the actual page data
            self.assertLessEqual(len(paginator.page), 5)
        else:
            # If no pagination, check total results
            self.assertLessEqual(queryset.count(), 5)

    def test_search_no_results_found(self):
        """Test search that finds no matching users."""
        request = self.create_mock_request(self.requesting_user)

        success, queryset, page_data, error_response = execute_user_search(
            search_query="nonexistentuser",
            requesting_user=self.requesting_user,
            request=request,
            view_instance=self.view,
            min_query_length=2,
            page_size=10
        )

        self.assertTrue(success)
        self.assertIsNotNone(queryset)
        self.assertIsNone(error_response)
        self.assertEqual(queryset.count(), 0)

    def test_search_with_whitespace_query(self):
        """Test search with query containing whitespace."""
        request = self.create_mock_request(self.requesting_user)

        success, queryset, page_data, error_response = execute_user_search(
            search_query="  john  ",
            requesting_user=self.requesting_user,
            request=request,
            view_instance=self.view,
            min_query_length=2,
            page_size=10
        )

        self.assertTrue(success)
        self.assertIsNotNone(queryset)
        self.assertIsNone(error_response)

        usernames = list(queryset.values_list('username', flat=True))
        self.assertIn("john_doe", usernames)

    def test_search_integration_with_all_steps(self):
        """Test that all search steps work together correctly."""
        # Set up a more complex scenario
        friend_user = User.objects.create_user(
            username="friend_user",
            first_name="Friend",
            last_name="User",
            email="friend@example.com"
        )

        # Make friend_user visible to friends only
        friend_user.profile.privacy_settings.search_visibility = 'friends_only'
        friend_user.profile.privacy_settings.save()

        # Make them friends
        self.requesting_user.profile.friends.add(friend_user)
        friend_user.profile.friends.add(self.requesting_user)

        request = self.create_mock_request(self.requesting_user)

        success, queryset, page_data, error_response = execute_user_search(
            search_query="friend",
            requesting_user=self.requesting_user,
            request=request,
            view_instance=self.view,
            min_query_length=2,
            page_size=10
        )

        self.assertTrue(success)
        self.assertIsNotNone(queryset)
        self.assertIsNone(error_response)

        usernames = list(queryset.values_list('username', flat=True))

        # Should find friend_user because they are friends
        self.assertIn("friend_user", usernames)
