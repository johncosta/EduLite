"""Mercury Performance Tests for UserProfileRetrieveUpdateView

This module contains performance tests for the UserProfileRetrieveUpdateView using
the Mercury intelligent performance testing framework.
"""

import sys
from pathlib import Path

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status

# Add performance testing framework to path
backend_path = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

from performance_testing.python_bindings.django_integration_mercury import DjangoMercuryAPITestCase
from users.models import UserProfile, ProfileFriendRequest, UserProfilePrivacySettings

User = get_user_model()



class UserProfileRetrieveUpdateViewMercuryTests(DjangoMercuryAPITestCase):
    """
    Performance test suite for the UserProfileRetrieveUpdateView using Mercury framework.
    
    Tests profile retrieval and update operations with focus on:
    - Query optimization for related objects
    - N+1 query detection
    - Memory efficiency for profile data serialization
    - Update operation performance
    """

    @classmethod
    def setUpClass(cls):
        """Configure Mercury for intelligent performance monitoring."""
        super().setUpClass()
        cls.configure_mercury(
            enabled=True,
            auto_scoring=True,
            store_history=True
        )
        
        # Set custom thresholds for profile operations
        cls.set_performance_thresholds({
            'response_time_ms': 100,   # Profile operations should be fast
            'query_count_max': 5,      # Profile + related objects
            'memory_overhead_mb': 20   # Profile data is relatively small
        })

    @classmethod
    def setUpTestData(cls):
        """Set up test data for performance testing."""
        # Create test users with complete profiles
        cls.user1 = User.objects.create_user(
            username="testuser1",
            password="password123",
            email="user1@example.com",
            first_name="Test",
            last_name="User1"
        )
        cls.profile1 = UserProfile.objects.get(user=cls.user1)
        cls.profile1.bio = "This is test user 1's bio"
        cls.profile1.date_of_birth = "1990-01-01"
        cls.profile1.country = "US"
        cls.profile1.save()
        
        cls.user2 = User.objects.create_user(
            username="testuser2",
            password="password123",
            email="user2@example.com",
            first_name="Test",
            last_name="User2"
        )
        cls.profile2 = UserProfile.objects.get(user=cls.user2)
        cls.profile2.bio = "This is test user 2's bio"
        cls.profile2.date_of_birth = "1991-02-02"
        cls.profile2.country = "UK"
        cls.profile2.save()
        
        # Create admin user
        cls.admin_user = User.objects.create_superuser(
            username="admin",
            password="adminpass123",
            email="admin@example.com"
        )
        cls.admin_profile = UserProfile.objects.get(user=cls.admin_user)
        
        # Add some friends for user1
        cls.friend1 = User.objects.create_user(
            username="friend1", password="password123"
        )
        cls.friend2 = User.objects.create_user(
            username="friend2", password="password123"
        )
        cls.profile1.friends.add(cls.friend1, cls.friend2)
        
        # URLs
        cls.profile1_url = reverse("userprofile-detail", kwargs={"pk": cls.profile1.pk})
        cls.profile2_url = reverse("userprofile-detail", kwargs={"pk": cls.profile2.pk})

    def test_retrieve_own_profile_performance(self):
        """Test performance of retrieving own profile."""
        self.client.force_authenticate(user=self.user1)
        
        # Mercury automatically monitors this request
        response = self.client.get(self.profile1_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.profile1.pk)
        self.assertEqual(response.data["bio"], "This is test user 1's bio")
        
        # Verify all expected fields are present
        expected_fields = {
            "id", "user", "bio", "date_of_birth", "profile_picture",
            "country", "languages", "website_url", "friends"
        }
        self.assertTrue(expected_fields.issubset(set(response.data.keys())))

    def test_retrieve_other_profile_performance(self):
        """Test performance of retrieving another user's profile."""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(self.profile2_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.profile2.pk)

    def test_admin_retrieve_profile_performance(self):
        """Test performance when admin retrieves any profile."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.profile1_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.profile1.pk)

    def test_update_own_profile_performance(self):
        """Test performance of updating own profile with PUT."""
        self.client.force_authenticate(user=self.user1)
        
        update_data = {
            "bio": "Updated bio for performance testing",
            "date_of_birth": "1990-06-15",
            "country": "CA",
            "languages": ["en", "fr"],
            "website_url": "https://example.com"
        }
        
        response = self.client.put(self.profile1_url, update_data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["bio"], "Updated bio for performance testing")
        self.assertEqual(response.data["country"], "CA")
        
        # Verify the update persisted
        self.profile1.refresh_from_db()
        self.assertEqual(self.profile1.bio, "Updated bio for performance testing")

    def test_partial_update_profile_performance(self):
        """Test performance of partial profile update with PATCH."""
        self.client.force_authenticate(user=self.user1)
        
        patch_data = {
            "bio": "Just updating the bio",
            "website_url": "https://newsite.com"
        }
        
        response = self.client.patch(self.profile1_url, patch_data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["bio"], "Just updating the bio")
        self.assertEqual(response.data["website_url"], "https://newsite.com")
        # Other fields should remain unchanged
        self.assertEqual(response.data["country"], "US")

    def test_profile_with_many_friends_performance(self):
        """Test performance with profiles having many friend relationships."""
        # Set custom thresholds for this test as it involves more data
        self.set_test_performance_thresholds({
            'response_time_ms': 150,
            'query_count_max': 10,  # More queries for friend relationships
            'memory_overhead_mb': 30
        })
        
        # Create a user with many friends
        popular_user = User.objects.create_user(
            username="popular_user",
            password="password123",
            email="popular@example.com"
        )
        popular_profile = UserProfile.objects.get(user=popular_user)
        popular_profile.bio = "I have many friends!"
        popular_profile.save()
        
        # Add 50 friends
        friends = []
        for i in range(50):
            friend = User.objects.create_user(
                username=f"friend_{i}",
                password="password123",
                email=f"friend{i}@example.com"
            )
            friends.append(friend)
        
        popular_profile.friends.add(*friends)
        
        # Test retrieval
        self.client.force_authenticate(user=popular_user)
        url = reverse("profile-retrieve-update", kwargs={"pk": popular_profile.pk})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["friends"]), 50)

    def test_profile_with_complex_data_performance(self):
        """Test performance with profiles containing all optional fields."""
        complex_user = User.objects.create_user(
            username="complex_user",
            password="password123",
            email="complex@example.com",
            first_name="Complex",
            last_name="User"
        )
        complex_profile = UserProfile.objects.get(user=complex_user)
        
        # Fill all profile fields
        complex_profile.bio = "A" * 500  # Long bio
        complex_profile.date_of_birth = "1985-05-05"
        complex_profile.country = "JP"
        complex_profile.languages = ["en", "ja", "es", "fr", "de"]
        complex_profile.website_url = "https://complexuser.example.com"
        complex_profile.save()
        
        # Add friends and friend requests
        for i in range(10):
            friend = User.objects.create_user(
                username=f"complex_friend_{i}",
                password="password123"
            )
            complex_profile.friends.add(friend)
            
            # Create some friend requests
            if i < 5:
                ProfileFriendRequest.objects.create(
                    sender=UserProfile.objects.get(user=friend),
                    receiver=complex_profile,
                    message=f"Request {i}"
                )
        
        self.client.force_authenticate(user=complex_user)
        url = reverse("profile-retrieve-update", kwargs={"pk": complex_profile.pk})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["bio"]), 500)
        self.assertEqual(len(response.data["languages"]), 5)
        self.assertEqual(len(response.data["friends"]), 10)

    def test_concurrent_profile_updates_performance(self):
        """Test performance of multiple profile updates in sequence."""
        self.client.force_authenticate(user=self.user1)
        
        # Perform multiple updates
        updates = [
            {"bio": "First update"},
            {"bio": "Second update", "country": "FR"},
            {"bio": "Third update", "languages": ["en", "fr", "es"]},
            {"website_url": "https://final.com"},
        ]
        
        for i, update_data in enumerate(updates):
            response = self.client.patch(self.profile1_url, update_data, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Verify the update
            for key, value in update_data.items():
                self.assertEqual(response.data[key], value)

    def test_invalid_update_performance(self):
        """Test performance when update validation fails."""
        self.client.force_authenticate(user=self.user1)
        
        # Try to update with invalid data
        invalid_data = {
            "bio": "B" * 1001,  # Exceeds max length (assuming 1000)
            "date_of_birth": "invalid-date",
            "country": "INVALID_COUNTRY_CODE"
        }
        
        response = self.client.put(self.profile1_url, invalid_data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("bio", response.data)  # Should have validation error for bio

    def test_unauthorized_update_performance(self):
        """Test performance when user tries to update another user's profile."""
        self.client.force_authenticate(user=self.user2)
        
        update_data = {
            "bio": "Trying to update someone else's profile"
        }
        
        response = self.client.patch(self.profile1_url, update_data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_profile_serialization_performance(self):
        """Test performance of profile serialization with nested data."""
        # Create a profile with all relationships
        rich_user = User.objects.create_user(
            username="rich_user",
            password="password123",
            email="rich@example.com"
        )
        rich_profile = UserProfile.objects.get(user=rich_user)
        
        # Add multiple relationships
        for i in range(20):
            friend = User.objects.create_user(
                username=f"rich_friend_{i}",
                password="password123"
            )
            rich_profile.friends.add(friend)
        
        self.client.force_authenticate(user=rich_user)
        url = reverse("profile-retrieve-update", kwargs={"pk": rich_profile.pk})
        
        # Test multiple retrievals to check caching/consistency
        for _ in range(3):
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["id"], rich_profile.pk)
            self.assertEqual(len(response.data["friends"]), 20)