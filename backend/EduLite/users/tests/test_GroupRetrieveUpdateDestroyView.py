from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class GroupRetrieveUpdateDestroyViewTests(APITestCase):
    """
    Tests for the GroupRetrieveUpdateDestroyView API endpoint.
    Verifies permissions (IsAdminUserOrReadOnly) and functionality for
    retrieving (GET), updating (PUT/PATCH), and deleting (DELETE) specific groups.
    """

    @classmethod
    def setUpTestData(cls):
        # Create users
        cls.non_admin_user = User.objects.create_user(
            username="testuser_rud", password="password123"
        )
        cls.admin_user = User.objects.create_superuser(
            username="admin_rud", password="password123"
        )

        # Create a group to be manipulated in tests
        cls.group_to_modify = Group.objects.create(name="Marketing Team")
        cls.group_to_modify_url = reverse(
            "group-detail", kwargs={"pk": cls.group_to_modify.pk}
        )

        cls.non_existent_group_pk = (
            cls.group_to_modify.pk + 100
        )  # A PK that likely doesn't exist
        cls.non_existent_group_url = reverse(
            "group-detail", kwargs={"pk": cls.non_existent_group_pk}
        )

        # URL for obtaining JWT tokens
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
        # Clear credentials after each test
        self.client.credentials()
        super().tearDown()

    # --- Test GET (Retrieve Specific Group) Operations ---

    def test_unauthenticated_user_cannot_retrieve_group(self):
        response = self.client.get(self.group_to_modify_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_non_admin_can_retrieve_group(self):
        token = self._get_jwt_token("testuser_rud", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(self.group_to_modify_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.group_to_modify.name)

    def test_admin_user_can_retrieve_group(self):
        token = self._get_jwt_token("admin_rud", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(self.group_to_modify_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.group_to_modify.name)

    def test_retrieve_non_existent_group_returns_404(self):
        token = self._get_jwt_token(
            "testuser_rud", "password123"
        )  # Any authenticated user
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(self.non_existent_group_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- Test PUT (Update Group) Operations ---

    def test_unauthenticated_user_cannot_put_group(self):
        data = {"name": "Updated Marketing Team (Unauth)"}
        response = self.client.put(self.group_to_modify_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_non_admin_cannot_put_group(self):
        token = self._get_jwt_token("testuser_rud", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        data = {"name": "Updated Marketing Team (NonAdmin)"}
        response = self.client.put(self.group_to_modify_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_put_group_with_valid_data(self):
        token = self._get_jwt_token("admin_rud", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        new_name = "Renamed Marketing Division"
        data = {
            "name": new_name
        }  # GroupSerializer only has 'name' and 'url' (read-only) as primary fields
        response = self.client.put(self.group_to_modify_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.group_to_modify.refresh_from_db()
        self.assertEqual(self.group_to_modify.name, new_name)

    def test_admin_user_put_group_with_invalid_data_returns_400(self):
        token = self._get_jwt_token("admin_rud", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        data = {}  # Invalid: 'name' is required
        response = self.client.put(self.group_to_modify_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_user_put_non_existent_group_returns_404(self):
        token = self._get_jwt_token("admin_rud", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        data = {"name": "Does Not Matter"}
        response = self.client.put(self.non_existent_group_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- Test PATCH (Partially Update Group) Operations ---
    # (Similar structure to PUT tests)

    def test_unauthenticated_user_cannot_patch_group(self):
        data = {"name": "Patched Name (Unauth)"}
        response = self.client.patch(self.group_to_modify_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_non_admin_cannot_patch_group(self):
        token = self._get_jwt_token("testuser_rud", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        data = {"name": "Patched Name (NonAdmin)"}
        response = self.client.patch(self.group_to_modify_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_patch_group_with_valid_data(self):
        token = self._get_jwt_token("admin_rud", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        new_name_partial = "Marketing Team - Patched"
        data = {"name": new_name_partial}
        response = self.client.patch(self.group_to_modify_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.group_to_modify.refresh_from_db()
        self.assertEqual(self.group_to_modify.name, new_name_partial)

    def test_admin_user_patch_non_existent_group_returns_404(self):
        token = self._get_jwt_token("admin_rud", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        data = {"name": "Patch To Nowhere"}
        response = self.client.patch(self.non_existent_group_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- Test DELETE (Delete Group) Operations ---

    def test_unauthenticated_user_cannot_delete_group(self):
        response = self.client.delete(self.group_to_modify_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_non_admin_cannot_delete_group(self):
        token = self._get_jwt_token("testuser_rud", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.delete(self.group_to_modify_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            Group.objects.filter(pk=self.group_to_modify.pk).exists()
        )  # Ensure not deleted

    def test_admin_user_can_delete_group(self):
        token = self._get_jwt_token("admin_rud", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.delete(self.group_to_modify_url)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertFalse(
            Group.objects.filter(pk=self.group_to_modify.pk).exists()
        )  # Ensure deleted

    def test_admin_user_delete_non_existent_group_returns_404(self):
        token = self._get_jwt_token("admin_rud", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.delete(self.non_existent_group_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
