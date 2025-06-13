import unittest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User


class UserUpdateDeleteViewTests(APITestCase):
    def setUp(self):
        # Admin user to make authenticated requests that should succeed
        self.admin_user = User.objects.create_superuser(
            username="admineditor",
            email="admineditor@example.com",
            password="password123",
        )
        # Regular user to test permission denial
        self.regular_user = User.objects.create_user(
            username="reguser", email="reguser@example.com", password="password123"
        )
        # Target user for update/delete operations
        self.target_user_for_edit = User.objects.create_user(
            username="usertoedit",
            email="toedit@example.com",
            password="password123",
            first_name="InitialFirst",
            last_name="InitialLast",
        )

        self.detail_url = reverse(
            "user-update", kwargs={"pk": self.target_user_for_edit.pk}
        )
        self.non_existent_pk = self.target_user_for_edit.pk + 999
        self.not_found_url = reverse("user-update", kwargs={"pk": self.non_existent_pk})

    # --- PUT (Update) Tests ---
    def test_admin_can_update_user_put(self):
        self.client.force_authenticate(user=self.admin_user)
        updated_data = {
            "username": "updatedbyadmin",
            "email": "updatedbyadmin@example.com",
        }
        response = self.client.put(self.detail_url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.target_user_for_edit.refresh_from_db()
        self.assertEqual(self.target_user_for_edit.username, updated_data["username"])
        self.assertEqual(self.target_user_for_edit.email, updated_data["email"])

    def test_regular_user_cannot_update_user_put(self):
        self.client.force_authenticate(user=self.regular_user)
        updated_data = {"email": "regattempt@example.com"}
        response = self.client.put(self.detail_url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_update_user_put(self):
        updated_data = {"email": "unauthattempt@example.com"}
        response = self.client.put(self.detail_url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_update_user_put_invalid_data(self):
        self.client.force_authenticate(user=self.admin_user)
        invalid_data = {
            "email": "notanemail"
        }  # Username is required by PUT if not provided
        response = self.client.put(self.detail_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "username", response.data
        )  # PUT requires all fields for a full update

    # --- PATCH (Partial Update) Tests ---
    def test_admin_can_partial_update_user_patch(self):
        self.client.force_authenticate(user=self.admin_user)
        patch_data = {"email": "patchedbyadmin@example.com"}
        response = self.client.patch(self.detail_url, patch_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.target_user_for_edit.refresh_from_db()
        self.assertEqual(self.target_user_for_edit.email, patch_data["email"])
        self.assertEqual(
            self.target_user_for_edit.username, "usertoedit"
        )  # Should remain unchanged

    def test_regular_user_cannot_partial_update_user_patch(self):
        self.client.force_authenticate(user=self.regular_user)
        patch_data = {"email": "regattempt_patch@example.com"}
        response = self.client.patch(self.detail_url, patch_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- DELETE Tests ---
    def test_admin_can_delete_user(self):
        self.client.force_authenticate(user=self.admin_user)
        initial_user_count = User.objects.count()
        response = self.client.delete(self.detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(User.objects.count(), initial_user_count - 1)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(pk=self.target_user_for_edit.pk)

    def test_regular_user_cannot_delete_user(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(self.detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_delete_user(self):
        response = self.client.delete(self.detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_delete_user_not_found(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.not_found_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
