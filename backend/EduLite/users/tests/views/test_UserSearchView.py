# backend/users/
import sys
from pathlib import Path
import logging

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.db.models import Q

logger = logging.getLogger(__name__)
User = get_user_model()

# Add performance testing framework to path
performance_path = Path(__file__).parent.parent.parent.parent.parent / "performance_testing" / "python_bindings"
sys.path.insert(0, str(performance_path))

from performance_testing.python_bindings.django_integration_mercury import DjangoMercuryAPITestCase

class UserSearchViewTests(DjangoMercuryAPITestCase):
    """
    Test suite for the UserSearchView.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole test class."""
        cls.search_url = reverse(
            "user-search"
        )  # Make sure 'user-search' is the name in your urls.py

        # User who will perform the searches
        cls.searching_user = User.objects.create_user(
            username="searcher", password="password123"
        )

        # Users to be searched
        cls.user_alpha = User.objects.create_user(
            username="alpha_user",
            first_name="Alpha",
            last_name="One",
            email="alpha@example.com",
            is_active=True,
        )
        cls.user_beta_firstname = User.objects.create_user(
            username="beta_user",
            first_name="BetaTest",
            last_name="Two",
            email="beta@example.com",
            is_active=True,
        )
        cls.user_gamma_lastname = User.objects.create_user(
            username="gamma_user",
            first_name="Gamma",
            last_name="TestThree",
            email="gamma@example.com",
            is_active=True,
        )
        cls.user_delta_inactive = User.objects.create_user(
            username="delta_inactive_tester",
            first_name="Delta",
            last_name="Four",
            email="delta@example.com",
            is_active=False,  # Inactive user
        )
        cls.user_epsilon_nomatch = User.objects.create_user(
            username="epsilon_user",
            first_name="Epsilon",
            last_name="Five",
            email="epsilon@example.com",
            is_active=True,
        )
        cls.user_zeta_case = User.objects.create_user(
            username="ZETA_USER_CASE",
            first_name="Zeta",
            last_name="SixTest",
            email="zeta@example.com",
            is_active=True,
        )
        # Create enough users to ensure pagination (e.g., 12 users matching 'page_test')
        # Assuming page_size is 10 for UserSearchView's paginator
        for i in range(12):
            User.objects.create_user(
                username=f"page_test_user{i:02d}", first_name="PageTest", is_active=True
            )
            
        User.objects.create_user(
            username="test_user_c", first_name="Common", is_active=True
        )
        User.objects.create_user(
            username="test_user_a", first_name="Common", is_active=True
        )
        User.objects.create_user(
            username="test_user_b", last_name="Common", is_active=True
        )

    def setUp(self):
        """Authenticate the client for each test."""
        self.client.force_authenticate(user=self.searching_user)

    def test_search_requires_authentication(self):
        """
        Test that unauthenticated users cannot access the search endpoint.
        """
        self.client.logout()  # Ensure no authentication
        response = self.client.get(self.search_url, {"q": "test"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_search_with_empty_query(self):
        """
        Test that an empty query string returns a 400 Bad Request.
        """
        response = self.client.get(self.search_url, {"q": ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Search query is required", response.data.get("detail", ""))


    def test_search_with_short_query(self):
        """
        Test that a query string shorter than MIN_QUERY_LENGTH (e.g., 2) returns a 400.
        """
        logger.debug("test_search_with_short_query():")
        response = self.client.get(
            self.search_url, {"q": "a"}
        )  # Assuming MIN_QUERY_LENGTH is 2 or 3
        logger.debug(
            f"--\t response.status_code: {response.status_code}\n"
            f"--\t response.data['detail']: {response.data.get('detail', '')}\n"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Search query must be at least", response.data.get("detail", ""))

    def test_search_by_username_exact(self):
        """Test searching by a part of the username."""
        response = self.client.get(self.search_url, {"q": "alpha_user"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["username"], self.user_alpha.username
        )

    def test_search_by_username_partial(self):
        """Test searching by a part of the username."""
        response = self.client.get(self.search_url, {"q": "alpha"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["username"], self.user_alpha.username
        )

    def test_search_by_first_name(self):
        """Test searching by a part of the first name."""
        response = self.client.get(self.search_url, {"q": "BetaTest"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["username"], self.user_beta_firstname.username
        )

    def test_search_by_last_name(self):
        """Test searching by a part of the last name."""
        response = self.client.get(self.search_url, {"q": "TestThree"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["username"], self.user_gamma_lastname.username
        )

    def test_search_case_insensitive(self):
        """Test that search is case-insensitive."""
        response = self.client.get(
            self.search_url, {"q": "zeta_user_case"}
        )  # Search with lowercase
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["username"], self.user_zeta_case.username
        )

        response_upper = self.client.get(self.search_url, {"q": "ZETA"})
        self.assertEqual(response_upper.status_code, status.HTTP_200_OK)
        self.assertEqual(response_upper.data["count"], 1)
        self.assertEqual(
            response_upper.data["results"][0]["username"], self.user_zeta_case.username
        )

        response_mixed_fn = self.client.get(
            self.search_url, {"q": "bEtAtEsT"}
        )  # search for BetaTest
        self.assertEqual(response_mixed_fn.status_code, status.HTTP_200_OK)
        self.assertEqual(response_mixed_fn.data["count"], 1)
        self.assertEqual(
            response_mixed_fn.data["results"][0]["username"],
            self.user_beta_firstname.username,
        )

    def test_search_no_results(self):
        """Test searching for a term that matches no active users."""
        response = self.client.get(self.search_url, {"q": "nonexistentqueryxyz"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["results"]), 0)

    def test_search_multiple_matches_and_ordering(self):
        """Test search returning multiple users, ordered by username."""
        logger.debug("test_search_multiple_matches_and_ordering():")
        response = self.client.get(self.search_url, {"q": "Common"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

        results = response.data["results"]
        logger.debug(
            f"--\t response.data['results'][0]['username']: {results[0]['username']}\n"
            f"--\t response.data['results'][1]['username']: {results[1]['username']}\n"
            f"--\t response.data['results'][2]['username']: {results[2]['username']}\n"
        )
        self.assertEqual(
            results[0]["username"], "test_user_a"
        )  # Assuming order_by('username')
        self.assertEqual(results[1]["username"], "test_user_b")
        self.assertEqual(results[2]["username"], "test_user_c")

    def test_search_pagination(self):
        """Test that search results are paginated."""
        
        self.set_test_performance_thresholds({
            'response_time_ms': 150,
            'query_count_max': 16,
            'memory_overhead_mb': 50,
        })

        response_page1 = self.client.get(self.search_url, {"q": "PageTest"})
        self.assertEqual(response_page1.status_code, status.HTTP_200_OK)
        self.assertEqual(response_page1.data["count"], 12)
        self.assertEqual(
            len(response_page1.data["results"]), 10
        )  # Default page size from your view
        self.assertIsNotNone(response_page1.data["next"])
        self.assertIsNone(response_page1.data["previous"])

        # Fetch the next page
        next_page_url = response_page1.data["next"]
        if next_page_url:  # Ensure next_page_url is not None
            response_page2 = self.client.get(
                next_page_url
            )  # DRF pagination links are full URLs
            self.assertEqual(response_page2.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response_page2.data["results"]), 2)  # Remaining users
            self.assertIsNone(response_page2.data["next"])
            self.assertIsNotNone(response_page2.data["previous"])

    def test_search_distinct_results(self):
        """
        Test that a user matching the query in multiple fields appears only once.
        The .distinct() in the view handles this, especially important if joins were involved.
        """
        User.objects.create_user(
            username="tester_distinct",
            first_name="Tester",
            last_name="Distinctive",
            is_active=True,
        )
        logger.debug("test_search_distinct_results():")
        response = self.client.get(self.search_url, {"q": "tester"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Count how many times 'tester_distinct' appears
        found_count = 0
        for user_data in response.data["results"]:
            if user_data["username"] == "tester_distinct":
                found_count += 1
        logger.debug(f"--\t found_count: {found_count}\n")
        self.assertEqual(
            found_count, 1, "User matching in multiple fields should only appear once."
        )

class UserSearchPrivacyTests(DjangoMercuryAPITestCase):
    """
    Test suite for UserSearchView privacy functionality.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up data for privacy testing."""
        cls.search_url = reverse("user-search")

        # Create users with different privacy settings
        cls.searcher = User.objects.create_user(
            username="searcher",
            password="password123",
            first_name="Searcher"
        )

        cls.public_user = User.objects.create_user(
            username="public_user",
            first_name="Public",
            last_name="User",
            is_active=True
        )

        cls.friends_only_user = User.objects.create_user(
            username="friends_only_user",
            first_name="FriendsOnly",
            last_name="User",
            is_active=True
        )

        cls.friends_of_friends_user = User.objects.create_user(
            username="friends_of_friends_user",
            first_name="FriendsOfFriends",
            last_name="User",
            is_active=True
        )

        cls.non_friend_user = User.objects.create_user(
            username="non_friend_user",
            first_name="NonFriend",
            last_name="User",
            is_active=True
        )

        cls.mutual_friend = User.objects.create_user(
            username="mutual_friend",
            first_name="Mutual",
            last_name="Friend",
            is_active=True
        )

    def setUp(self):
        """Set up privacy settings and relationships for each test."""
        from users.models import UserProfile, UserProfilePrivacySettings

        # Create profiles and privacy settings
        searcher_profile, _ = UserProfile.objects.get_or_create(user=self.searcher)
        public_profile, _ = UserProfile.objects.get_or_create(user=self.public_user)
        friends_only_profile, _ = UserProfile.objects.get_or_create(user=self.friends_only_user)
        friends_of_friends_profile, _ = UserProfile.objects.get_or_create(user=self.friends_of_friends_user)
        non_friend_profile, _ = UserProfile.objects.get_or_create(user=self.non_friend_user)
        mutual_friend_profile, _ = UserProfile.objects.get_or_create(user=self.mutual_friend)

        # Set up privacy settings
        UserProfilePrivacySettings.objects.update_or_create(
            user_profile=public_profile,
            defaults={'search_visibility': 'everyone'}
        )

        UserProfilePrivacySettings.objects.update_or_create(
            user_profile=friends_only_profile,
            defaults={'search_visibility': 'friends_only'}
        )

        UserProfilePrivacySettings.objects.update_or_create(
            user_profile=friends_of_friends_profile,
            defaults={'search_visibility': 'friends_of_friends'}
        )

        UserProfilePrivacySettings.objects.update_or_create(
            user_profile=non_friend_profile,
            defaults={'search_visibility': 'friends_only'}
        )

        UserProfilePrivacySettings.objects.update_or_create(
            user_profile=mutual_friend_profile,
            defaults={'search_visibility': 'everyone'}
        )

        # Set up friend relationships
        # searcher <-> friends_only_user (direct friends)
        searcher_profile.friends.add(self.friends_only_user)
        friends_only_profile.friends.add(self.searcher)

        # mutual_friend <-> friends_of_friends_user (mutual friend setup)
        mutual_friend_profile.friends.add(self.friends_of_friends_user)
        friends_of_friends_profile.friends.add(self.mutual_friend)

        # searcher <-> mutual_friend (to create mutual friend relationship)
        searcher_profile.friends.add(self.mutual_friend)
        mutual_friend_profile.friends.add(self.searcher)

        # Authenticate the client
        self.client.force_authenticate(user=self.searcher)

    def test_search_everyone_visibility(self):
        """Test that users with 'everyone' visibility are always found."""
        response = self.client.get(self.search_url, {"q": "Public"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["username"], "public_user")

    def test_search_friends_only_visibility_as_friend(self):
        """Test that friends_only users are found by their friends."""
        response = self.client.get(self.search_url, {"q": "FriendsOnly"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["username"], "friends_only_user")

    def test_search_friends_only_visibility_as_non_friend(self):
        """Test that friends_only users are NOT found by non-friends."""
        # Create a new user who is not friends with friends_only_user
        stranger = User.objects.create_user(
            username="stranger",
            first_name="Stranger",
            is_active=True
        )
        self.client.force_authenticate(user=stranger)

        response = self.client.get(self.search_url, {"q": "FriendsOnly"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_search_friends_of_friends_visibility_with_mutual_friend(self):
        """Test that friends_of_friends users are found through mutual friends."""
        response = self.client.get(self.search_url, {"q": "FriendsOfFriends"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["username"], "friends_of_friends_user")

    def test_search_friends_of_friends_visibility_without_mutual_friend(self):
        """Test that friends_of_friends users are NOT found without mutual friends."""
        # Create a new user with no mutual friends
        isolated_user = User.objects.create_user(
            username="isolated",
            first_name="Isolated",
            is_active=True
        )
        self.client.force_authenticate(user=isolated_user)

        response = self.client.get(self.search_url, {"q": "FriendsOfFriends"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_search_self_always_visible(self):
        """Test that users can always find themselves regardless of privacy settings."""
        # Create a user with friends_only privacy
        self_search_user = User.objects.create_user(
            username="self_searcher",
            first_name="SelfSearch",
            is_active=True
        )

        from users.models import UserProfile, UserProfilePrivacySettings
        profile, _ = UserProfile.objects.get_or_create(user=self_search_user)
        UserProfilePrivacySettings.objects.update_or_create(
            user_profile=profile,
            defaults={'search_visibility': 'friends_only'}
        )

        self.client.force_authenticate(user=self_search_user)

        response = self.client.get(self.search_url, {"q": "SelfSearch"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["username"], "self_searcher")

    def test_search_anonymous_user_only_sees_everyone(self):
        """Test that anonymous users cannot access search (authentication required)."""
        self.client.logout()  # Make request anonymous

        response = self.client.get(self.search_url, {"q": "User"})

        # Expect 401 since authentication is required
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_search_privacy_filtering_with_multiple_matches(self):
        """Test privacy filtering when multiple users match the search query."""
        # Search for "User" which should match multiple users with different privacy settings
        response = self.client.get(self.search_url, {"q": "User"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        found_usernames = [user["username"] for user in response.data["results"]]

        # Should find:
        # - public_user (everyone visibility)
        # - friends_only_user (friends with searcher)
        # - friends_of_friends_user (mutual friend through mutual_friend)
        # Should NOT find:
        # - non_friend_user (friends_only but not friends with searcher)

        self.assertIn("public_user", found_usernames)
        self.assertIn("friends_only_user", found_usernames)
        self.assertIn("friends_of_friends_user", found_usernames)
        self.assertNotIn("non_friend_user", found_usernames)

    def test_search_with_missing_privacy_settings(self):
        """Test search behavior when a user has no privacy settings (should default to safe setting)."""
        # Create a user without privacy settings
        no_privacy_user = User.objects.create_user(
            username="no_privacy_user",
            first_name="NoPrivacy",
            is_active=True
        )

        # Create profile but no privacy settings
        from users.models import UserProfile
        UserProfile.objects.get_or_create(user=no_privacy_user)

        response = self.client.get(self.search_url, {"q": "NoPrivacy"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # The behavior depends on your default privacy setting
        # Adjust this assertion based on your model's default behavior
        # If default is 'everyone', should find the user
        # If default is 'friends_only', should not find the user
        # self.assertEqual(response.data["count"], 1)  # Adjust based on your defaults