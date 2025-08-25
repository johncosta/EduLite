# users/tests/views/test_UserProfilePrivacySettingsRetrieveUpdateView.py - Tests for UserProfilePrivacySettingsRetrieveUpdateView

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

from .. import UsersAppTestCase


class UserProfilePrivacySettingsRetrieveUpdateViewTest(UsersAppTestCase):
    """Test cases for the UserProfilePrivacySettingsRetrieveUpdateView API endpoint."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        # Privacy settings URL operates on current authenticated user
        self.url = reverse('privacy-settings')
        
    # --- Authentication Tests ---
    
    def test_retrieve_privacy_settings_requires_authentication(self):
        """Test that retrieving privacy settings requires authentication."""
        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_401_UNAUTHORIZED)
        
    def test_update_privacy_settings_requires_authentication(self):
        """Test that updating privacy settings requires authentication."""
        response = self.client.patch(self.url, {'search_visibility': 'nobody'})
        self.assert_response_success(response, status.HTTP_401_UNAUTHORIZED)
        
    # --- Retrieve Tests ---
    
    def test_retrieve_own_privacy_settings_success(self):
        """Test that users can retrieve their own privacy settings."""
        self.authenticate_as(self.ahmad)
        
        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)
        
        # Should get privacy settings data (specific fields tested in serializer tests)
        self.assertIsInstance(response.data, dict)
        self.assertGreater(len(response.data), 0)
        
    def test_retrieve_privacy_settings_for_different_users(self):
        """Test that each user retrieves their own privacy settings."""
        # Test Ahmad's settings
        self.authenticate_as(self.ahmad)
        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data['search_visibility'], 'friends_of_friends')
        
        # Test Sophie's settings (different user)
        self.authenticate_as(self.sophie)
        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data['search_visibility'], 'nobody')
        self.assertEqual(response.data['allow_friend_requests'], False)
        
    def test_privacy_settings_created_if_missing(self):
        """Test that privacy settings are created if they don't exist."""
        # Create a new user without privacy settings
        new_user = self.create_test_user(username="new_user_no_privacy")
        
        # Delete privacy settings if they exist (due to signal)
        if hasattr(new_user.profile, 'privacy_settings'):
            new_user.profile.privacy_settings.delete()
            
        self.authenticate_as(new_user)
        
        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)
        
        # Should have default settings
        self.assertIn('search_visibility', response.data)
        
        # Verify settings were created
        new_user.profile.refresh_from_db()
        self.assertTrue(hasattr(new_user.profile, 'privacy_settings'))
        
    # --- Update Tests ---
    
    def test_update_own_privacy_settings_success(self):
        """Test that users can update their own privacy settings."""
        self.authenticate_as(self.ahmad)
        
        response = self.client.patch(self.url, {
            'search_visibility': 'everyone',
            'profile_visibility': 'public',
            'show_email': True
        })
        
        self.assert_response_success(response, status.HTTP_200_OK)
        
        # Verify changes
        self.ahmad.profile.privacy_settings.refresh_from_db()
        self.assertEqual(self.ahmad.profile.privacy_settings.search_visibility, 'everyone')
        self.assertEqual(self.ahmad.profile.privacy_settings.profile_visibility, 'public')
        self.assertEqual(self.ahmad.profile.privacy_settings.show_email, True)
        
    def test_each_user_updates_own_settings(self):
        """Test that users can only update their own settings."""
        # Ahmad updates his settings
        self.authenticate_as(self.ahmad)
        response = self.client.patch(self.url, {
            'search_visibility': 'nobody'
        })
        self.assert_response_success(response, status.HTTP_200_OK)
        
        # Verify Ahmad's settings changed
        self.ahmad.profile.privacy_settings.refresh_from_db()
        self.assertEqual(self.ahmad.profile.privacy_settings.search_visibility, 'nobody')
        
        # Marie's settings should be unchanged
        self.marie.profile.privacy_settings.refresh_from_db()
        self.assertEqual(self.marie.profile.privacy_settings.search_visibility, 'everyone')
        
    # --- Validation Tests ---
    
    def test_update_privacy_settings_invalid_visibility(self):
        """Test updating with invalid visibility values."""
        self.authenticate_as(self.ahmad)
        
        # Try invalid search visibility
        response = self.client.patch(self.url, {
            'search_visibility': 'invalid_option'
        })
        self.assert_response_success(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('search_visibility', response.data)
        
    def test_update_privacy_settings_invalid_profile_visibility(self):
        """Test updating with invalid profile visibility."""
        self.authenticate_as(self.ahmad)
        
        response = self.client.patch(self.url, {
            'profile_visibility': 'super_private'
        })
        self.assert_response_success(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('profile_visibility', response.data)
        
    def test_update_privacy_settings_boolean_fields(self):
        """Test updating boolean privacy fields."""
        self.authenticate_as(self.ahmad)
        
        # Test with various boolean values
        response = self.client.patch(self.url, {
            'show_full_name': False,
            'show_email': True,
            'allow_friend_requests': False
        })
        
        self.assert_response_success(response, status.HTTP_200_OK)
        
        # Verify changes
        self.ahmad.profile.privacy_settings.refresh_from_db()
        self.assertEqual(self.ahmad.profile.privacy_settings.show_full_name, False)
        self.assertEqual(self.ahmad.profile.privacy_settings.show_email, True)
        self.assertEqual(self.ahmad.profile.privacy_settings.allow_friend_requests, False)
        
    # --- Partial Update Tests ---
    
    def test_partial_update_privacy_settings(self):
        """Test partial updates to privacy settings."""
        self.authenticate_as(self.ahmad)
        
        # Update only one field
        response = self.client.patch(self.url, {
            'show_email': True
        })
        
        self.assert_response_success(response, status.HTTP_200_OK)
        
        # Verify only that field changed
        self.ahmad.profile.privacy_settings.refresh_from_db()
        self.assertEqual(self.ahmad.profile.privacy_settings.show_email, True)
        # Other fields unchanged
        self.assertEqual(self.ahmad.profile.privacy_settings.search_visibility, 'friends_of_friends')
        
    # --- Full Update Tests ---
    
    def test_full_update_privacy_settings(self):
        """Test full updates to privacy settings."""
        self.authenticate_as(self.ahmad)
        
        # Get current settings
        response = self.client.get(self.url)
        current_data = response.data
        
        # Update all fields
        current_data.update({
            'search_visibility': 'nobody',
            'profile_visibility': 'private',
            'show_full_name': False,
            'show_email': False,
            'allow_friend_requests': False
        })
        
        response = self.client.put(self.url, current_data)
        self.assert_response_success(response, status.HTTP_200_OK)
        
        # Verify all changes
        self.ahmad.profile.privacy_settings.refresh_from_db()
        self.assertEqual(self.ahmad.profile.privacy_settings.search_visibility, 'nobody')
        self.assertEqual(self.ahmad.profile.privacy_settings.profile_visibility, 'private')
        self.assertEqual(self.ahmad.profile.privacy_settings.show_full_name, False)
        self.assertEqual(self.ahmad.profile.privacy_settings.show_email, False)
        self.assertEqual(self.ahmad.profile.privacy_settings.allow_friend_requests, False)
        
    # --- Read-only Fields Test ---
    
    def test_cannot_update_read_only_fields(self):
        """Test that read-only fields are ignored in updates."""
        self.authenticate_as(self.ahmad)
        
        response = self.client.patch(self.url, {
            'profile': self.marie.profile.id,  # Should be read-only
            'created_at': '2024-01-01T00:00:00Z',  # Should be read-only
            'show_email': True  # Valid field
        })
        
        self.assert_response_success(response, status.HTTP_200_OK)
        
        # Verify only valid field was updated
        self.ahmad.profile.privacy_settings.refresh_from_db()
        self.assertEqual(self.ahmad.profile.privacy_settings.show_email, True)
        self.assertEqual(self.ahmad.profile.privacy_settings.user_profile.id, self.ahmad.profile.id)
        
    # --- Privacy Setting Combinations ---
    
    def test_valid_privacy_setting_combinations(self):
        """Test various valid combinations of privacy settings."""
        self.authenticate_as(self.ahmad)
        
        # Test restrictive combination
        response = self.client.patch(self.url, {
            'search_visibility': 'nobody',
            'profile_visibility': 'private',
            'allow_friend_requests': False
        })
        self.assert_response_success(response, status.HTTP_200_OK)
        
        # Test open combination
        response = self.client.patch(self.url, {
            'search_visibility': 'everyone',
            'profile_visibility': 'public',
            'allow_friend_requests': True
        })
        self.assert_response_success(response, status.HTTP_200_OK)
        
        # Test friends-only combination
        response = self.client.patch(self.url, {
            'search_visibility': 'friends_only',
            'profile_visibility': 'friends_only',
            'allow_friend_requests': True
        })
        self.assert_response_success(response, status.HTTP_200_OK)
        
    # --- Admin Access Test ---
    
    def test_admin_accesses_own_privacy_settings(self):
        """Test that admin users also access their own settings, not others'."""
        # Make sarah_teacher an admin
        self.sarah_teacher.is_superuser = True
        self.sarah_teacher.is_staff = True
        self.sarah_teacher.save()
        
        self.authenticate_as(self.sarah_teacher)
        
        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)
        
        # Should get Sarah's settings, not anyone else's
        self.assertEqual(response.data['search_visibility'], 'everyone')  # Sarah's default
        
        # Update should affect Sarah's settings
        response = self.client.patch(self.url, {
            'search_visibility': 'friends_only'
        })
        self.assert_response_success(response, status.HTTP_200_OK)
        
        self.sarah_teacher.profile.privacy_settings.refresh_from_db()
        self.assertEqual(self.sarah_teacher.profile.privacy_settings.search_visibility, 'friends_only')
        
    # --- Performance Test ---
    
    def test_privacy_settings_update_performance(self):
        """Test performance of privacy settings updates."""
        self.authenticate_as(self.ahmad)
        
        import time
        start_time = time.time()
        
        # Make multiple updates
        for i in range(5):
            response = self.client.patch(self.url, {
                'show_email': i % 2 == 0,  # Toggle between True/False
                'show_full_name': i % 2 == 1
            })
            self.assert_response_success(response, status.HTTP_200_OK)
            
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete quickly
        self.assertLess(duration, 2.0, "Privacy settings update too slow")