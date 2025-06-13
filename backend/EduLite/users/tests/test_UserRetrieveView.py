import unittest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User


class UserRetrieveViewTests(APITestCase):  # Renamed to match the view
    def setUp(self):
        """
        Set up initial data:
        - self.requesting_user: An authenticated user to make requests.
        - self.target_user: The user whose data will be retrieved.
        """
        self.requesting_user = User.objects.create_user(
            username="requester_ret",
            email="requester_ret@example.com",
            password="password123",
        )
        self.target_user = User.objects.create_user(
            username="targetuser_ret",
            email="target_ret@example.com",
            password="password123",
            first_name="TargetToRetrieve",
            last_name="UserToRetrieve",
        )

        self.detail_url = reverse("user-detail", kwargs={"pk": self.target_user.pk})

        self.non_existent_pk = self.target_user.pk + 999  # A PK that won't exist
        self.not_found_url = reverse("user-detail", kwargs={"pk": self.non_existent_pk})

    # --- Retrieve (GET) Tests ---
    def test_retrieve_user_success(self):
        """Ensure an authenticated user can retrieve another user's details."""
        self.client.force_authenticate(user=self.requesting_user)
        response = self.client.get(self.detail_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data["username"], self.target_user.username)
        self.assertEqual(response.data["email"], self.target_user.email)
        # UserSerializer is Hyperlinked, so it should include 'url'
        self.assertIn("url", response.data)

    def test_retrieve_user_not_found(self):
        """Test retrieving a user that does not exist results in a 404."""
        self.client.force_authenticate(user=self.requesting_user)
        response = self.client.get(self.not_found_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_user_unauthenticated(self):
        """Ensure unauthenticated users cannot retrieve user details."""
        # No self.client.force_authenticate()
        response = self.client.get(self.detail_url, format="json")
        # Expecting 401 for JWT based auth (as per your IsAuthenticated permission class)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Test that other methods are not allowed ---
    def test_put_method_not_allowed(self):
        """Ensure PUT requests are not allowed (HTTP 405)."""
        self.client.force_authenticate(user=self.requesting_user)
        response = self.client.put(
            self.detail_url, {"email": "new@example.com"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_method_not_allowed(self):
        """Ensure PATCH requests are not allowed (HTTP 405)."""
        self.client.force_authenticate(user=self.requesting_user)
        response = self.client.patch(
            self.detail_url, {"email": "new@example.com"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_method_not_allowed(self):
        """Ensure DELETE requests are not allowed (HTTP 405)."""
        self.client.force_authenticate(user=self.requesting_user)
        response = self.client.delete(self.detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
