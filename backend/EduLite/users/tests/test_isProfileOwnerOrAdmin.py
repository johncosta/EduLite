from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import UserProfile

User = get_user_model()


class UserProfilePermissionsIntegrationTests(APITestCase):
    """
    Integration tests for UserProfileRetrieveUpdateView focusing on
    IsProfileOwnerOrAdmin permission logic, using JWT authentication.
    """

    @classmethod
    def setUpTestData(cls):
        # Create users and profiles once for the test class for efficiency
        cls.user1 = User.objects.create_user(
            username="user1", password="password123", email="user1@example.com"
        )
        cls.profile1 = cls.user1.profile
        cls.profile1_data = {"bio": "User1 original bio", "occupation": "Tester"}
        cls.profile1.bio = cls.profile1_data["bio"]
        cls.profile1.occupation = cls.profile1_data["occupation"]
        cls.profile1.save()
        cls.profile1_url = reverse("userprofile-detail", kwargs={"pk": cls.profile1.pk})

        cls.user2 = User.objects.create_user(
            username="user2", password="password123", email="user2@example.com"
        )
        cls.profile2 = cls.user2.profile
        cls.profile2_data = {"bio": "User2 original bio", "country": "Canada"}
        cls.profile2.bio = cls.profile2_data["bio"]
        cls.profile2.country = cls.profile2_data["country"]
        cls.profile2.save()
        cls.profile2_url = reverse("userprofile-detail", kwargs={"pk": cls.profile2.pk})

        # Make user1 and user2 friends so they can see each other's profiles
        cls.profile1.friends.add(cls.user2)
        cls.profile2.friends.add(cls.user1)

        cls.admin_user = User.objects.create_superuser(
            username="adminuser", password="password123", email="admin@example.com"
        )
        cls.admin_profile = cls.admin_user.profile
        cls.admin_profile_url = reverse(
            "userprofile-detail", kwargs={"pk": cls.admin_profile.pk}
        )

        cls.update_data = {
            "bio": "This is an updated bio.",
            "occupation": "Developer",
            "country": "USA",
        }

        # URL for obtaining JWT tokens (adjust 'token_obtain_pair' if your URL name is different)
        cls.token_obtain_url = reverse("token_obtain_pair")

    def _get_jwt_token(self, username, password):
        """Helper method to obtain JWT token."""
        response = self.client.post(
            self.token_obtain_url,
            {"username": username, "password": password},
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            f"Failed to obtain token for {username}",
        )
        return response.data["access"]

    def tearDown(self):
        # Clear credentials after each test to ensure isolation
        self.client.credentials()
        super().tearDown()

    # --- Test GET (View) Operations ---

    def test_unauthenticated_user_cannot_view_profile(self):
        response = self.client.get(self.profile1_url)
        # This should still be 401 as no auth is provided
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_view_own_profile(self):
        token = self._get_jwt_token("user1", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(self.profile1_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["bio"], self.profile1_data["bio"])

    def test_authenticated_user_can_view_other_profile(self):
        token = self._get_jwt_token("user1", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(self.profile2_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["bio"], self.profile2_data["bio"])

    def test_admin_can_view_any_profile(self):
        token = self._get_jwt_token("adminuser", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(self.profile1_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["bio"], self.profile1_data["bio"])

    # --- Test PATCH (Partial Update) Operations ---

    def test_unauthenticated_user_cannot_patch_profile(self):
        response = self.client.patch(self.profile1_url, self.update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_cannot_patch_other_users_profile(self):
        token = self._get_jwt_token("user1", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.patch(self.profile2_url, self.update_data, format="json")
        # Now this should correctly be 403 Forbidden as user1 is authenticated but not authorized
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.profile2.refresh_from_db()
        self.assertEqual(self.profile2.bio, self.profile2_data["bio"])

    def test_authenticated_user_can_patch_own_profile(self):
        token = self._get_jwt_token("user1", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        data_to_update = {"bio": "User1 new bio via PATCH"}
        response = self.client.patch(self.profile1_url, data_to_update, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile1.refresh_from_db()
        self.assertEqual(self.profile1.bio, data_to_update["bio"])
        self.assertEqual(self.profile1.occupation, self.profile1_data["occupation"])

    def test_admin_user_can_patch_other_users_profile(self):
        token = self._get_jwt_token("adminuser", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        data_to_update = {"occupation": "other"}
        response = self.client.patch(self.profile1_url, data_to_update, format="json")

        if response.status_code == status.HTTP_400_BAD_REQUEST:
            print(f"--- Failing Test: {self.id()} ---")  # self.id() gives the test name
            print("Request Data Sent:", data_to_update)
            print(
                "Response Content (Errors):", response.content.decode()
            )  # Or response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile1.refresh_from_db()
        self.assertEqual(self.profile1.occupation, data_to_update["occupation"])
        self.assertEqual(self.profile1.bio, self.profile1_data["bio"])

    # --- Test PUT (Full Update) Operations ---

    def test_unauthenticated_user_cannot_put_profile(self):
        response = self.client.put(self.profile1_url, self.update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_cannot_put_other_users_profile(self):
        token = self._get_jwt_token("user1", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        put_data = self.update_data.copy()
        response = self.client.put(self.profile2_url, put_data, format="json")
        # this should correctly be 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.profile2.refresh_from_db()
        self.assertEqual(self.profile2.bio, self.profile2_data["bio"])

    def test_authenticated_user_can_put_own_profile(self):
        token = self._get_jwt_token("user1", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        put_data = {
            "bio": "User1's complete new bio via PUT",
            "occupation": "trainer",
            "country": self.profile1.country,
            "preferred_language": self.profile1.preferred_language,
            "secondary_language": self.profile1.secondary_language,
        }
        response = self.client.put(self.profile1_url, put_data, format="json")

        if response.status_code == status.HTTP_400_BAD_REQUEST:
            print(f"--- Failing Test: {self.id()} ---")  # self.id() gives the test name
            print("Request Data Sent:", put_data)
            print(
                "Response Content (Errors):", response.content.decode()
            )  # Or response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile1.refresh_from_db()
        self.assertEqual(self.profile1.bio, put_data["bio"])
        self.assertEqual(self.profile1.occupation, put_data["occupation"])

    def test_admin_user_can_put_other_users_profile(self):
        token = self._get_jwt_token("adminuser", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        put_data = {
            "bio": "Admin updated User1's bio via PUT",
            "occupation": "mentor",
            "country": self.profile1.country,
            "preferred_language": self.profile1.preferred_language,
            "secondary_language": self.profile1.secondary_language,
        }
        response = self.client.put(self.profile1_url, put_data, format="json")

        if response.status_code == status.HTTP_400_BAD_REQUEST:
            print(f"--- Failing Test: {self.id()} ---")  # self.id() gives the test name
            print("Request Data Sent:", put_data)
            print(
                "Response Content (Errors):", response.content.decode()
            )  # Or response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile1.refresh_from_db()
        self.assertEqual(self.profile1.bio, put_data["bio"])
        self.assertEqual(self.profile1.occupation, put_data["occupation"])
