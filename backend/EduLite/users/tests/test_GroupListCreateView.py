from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class GroupListCreateViewTests(APITestCase):
    """
    Tests for the GroupListCreateView API endpoint.
    Verifies permissions (IsAdminUserOrReadOnly) and functionality for
    listing (GET) and creating (POST) groups.
    """

    @classmethod
    def setUpTestData(cls):
        # Create users
        cls.non_admin_user = User.objects.create_user(
            username="testuser", password="password123"
        )
        cls.admin_user = User.objects.create_superuser(
            username="admin", password="password123"
        )

        # Create some initial groups for listing tests
        cls.group1 = Group.objects.create(name="Editors")
        cls.group2 = Group.objects.create(name="Viewers")

        # URL for the GroupListCreateView
        cls.list_create_url = reverse("group-list-create")  # Example name

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

    # --- Test GET (List Groups) Operations ---

    def test_unauthenticated_user_cannot_list_groups(self):
        response = self.client.get(self.list_create_url)
        # IsAdminUserOrReadOnly first checks for authentication
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_non_admin_can_list_groups(self):
        token = self._get_jwt_token("testuser", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assuming paginated response; check if results are present
        self.assertIn("results", response.data)  # For paginated list
        self.assertEqual(
            len(response.data["results"]), 2
        )  # Check if both groups are listed
        self.assertTrue(
            any(g["name"] == self.group1.name for g in response.data["results"])
        )

    def test_admin_user_can_list_groups(self):
        token = self._get_jwt_token("admin", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 2)

    # --- Test POST (Create Group) Operations ---

    def test_unauthenticated_user_cannot_create_group(self):
        data = {"name": "New Group Unauth"}
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_non_admin_cannot_create_group(self):
        token = self._get_jwt_token("testuser", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        data = {"name": "New Group By NonAdmin"}
        response = self.client.post(self.list_create_url, data, format="json")
        # IsAdminUserOrReadOnly denies POST for non-admins
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_create_group_with_valid_data(self):
        token = self._get_jwt_token("admin", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        group_name = "Moderators_By_Admin"
        data = {"name": group_name}
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], group_name)

        self.assertIn("url", response.data)
        self.assertIn("id", response.data)
        self.assertTrue(isinstance(response.data["id"], int))

        self.assertTrue(Group.objects.filter(name=group_name).exists())

    def test_admin_user_cannot_create_group_with_invalid_data(self):
        token = self._get_jwt_token("admin", "password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        data = {}  # Invalid: 'name' is required for Group model
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)  # Check for error message on 'name' field
