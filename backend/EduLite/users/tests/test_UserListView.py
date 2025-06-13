from django.urls import reverse
import unittest
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.conf import settings
from django.test import override_settings


class UserListViewTests(APITestCase):
    def setUp(self):
        """
        Set up initial data for the tests.
        This includes an admin user, regular active users, and an inactive user.
        """
        self.list_url = reverse("user-list")

        self.admin_user = User.objects.create_superuser(
            username="testadmin", email="admin@example.com", password="password123"
        )
        self.user1 = User.objects.create_user(
            username="testuser1",
            email="user1@example.com",
            password="password123",
            first_name="Regular",
            last_name="UserOne",
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email="user2@example.com",
            password="password123",
            first_name="Another",
            last_name="UserTwo",
        )
        self.inactive_user = User.objects.create_user(
            username="inactiveuser",
            email="inactive@example.com",
            password="password123",
            is_active=False,  # This user is inactive
        )

        # Total users created that User.objects.all() should find
        self.total_users_in_db = 4

    def test_list_users_as_admin_shows_all_users(self):
        """
        Test if an authenticated admin user can retrieve the list of ALL users,
        including inactive ones, as per User.objects.all().
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        # Check pagination structure and count
        self.assertIn(
            "count",
            response.data,
            "Response should contain a 'count' field for pagination.",
        )
        self.assertIn(
            "results",
            response.data,
            "Response should contain a 'results' field for paginated data.",
        )

        self.assertEqual(
            response.data["count"],
            self.total_users_in_db,
            f"Expected {self.total_users_in_db} users, but API returned count of {response.data.get('count')}. "
            "This indicates not all users from User.objects.all() are being listed.",
        )

        returned_usernames = sorted(
            [item["username"] for item in response.data["results"]]
        )
        expected_usernames = sorted(
            [
                self.admin_user.username,
                self.user1.username,
                self.user2.username,
                self.inactive_user.username,
            ]
        )

        # If count is correct, it strongly suggests the underlying queryset is User.objects.all().
        if len(response.data["results"]) == self.total_users_in_db:
            self.assertListEqual(
                returned_usernames,
                expected_usernames,
                "The usernames in the response do not match all expected usernames.",
            )

    def test_list_users_as_regular_authenticated_user(self):
        """
        Test if a regular authenticated user can also see all users.
        Note: Your current UserListView (inheriting IsAuthenticated) allows this.
        Consider if this is desired behavior or if it should be admin-only.
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(
            response.data["count"],
            self.total_users_in_db,
            "A regular authenticated user should also see all users based on current view logic and User.objects.all().",
        )

    def test_unauthenticated_user_cannot_list_users(self):
        """
        Test that an unauthenticated request to list users is denied.
        (Expect 401 if JWT is default, or 403 for some other schemes like Session if not logged in).
        """
        response = self.client.get(self.list_url, format="json")
        # If your DEFAULT_AUTHENTICATION_CLASSES is simplejwt, it should be 401
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED, response.data
        )
