# backend/EduLite/users/tests/test_UserProfilePrivacySettingsChoicesView.py
# Tests for UserProfilePrivacySettingsChoicesView

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class UserProfilePrivacySettingsChoicesViewTests(APITestCase):
    """
    Test suite for UserProfilePrivacySettingsChoicesView.
    Tests the API endpoint that returns available privacy setting choices.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole test class."""
        cls.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )

        # URL pattern - adjust based on your actual URL configuration
        cls.choices_url = reverse("privacy-settings-choices")

    def setUp(self):
        """Set up for each test method."""
        self.client.force_authenticate(user=self.user)

    def test_requires_authentication(self):
        """Test that the view requires authentication."""
        self.client.logout()

        response = self.client.get(self.choices_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_privacy_choices_success(self):
        """Test successful retrieval of privacy setting choices."""
        response = self.client.get(self.choices_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that response contains the expected top-level keys
        self.assertIn('search_visibility_choices', response.data)
        self.assertIn('profile_visibility_choices', response.data)

    def test_search_visibility_choices_format(self):
        """Test that search visibility choices have correct format."""
        response = self.client.get(self.choices_url)

        search_choices = response.data['search_visibility_choices']

        # Should be a list
        self.assertIsInstance(search_choices, list)

        # Should have at least one choice
        self.assertGreater(len(search_choices), 0)

        # Each choice should have 'value' and 'label' keys
        for choice in search_choices:
            self.assertIn('value', choice)
            self.assertIn('label', choice)
            self.assertIsInstance(choice['value'], str)
            self.assertIsInstance(choice['label'], str)

    def test_profile_visibility_choices_format(self):
        """Test that profile visibility choices have correct format."""
        response = self.client.get(self.choices_url)

        profile_choices = response.data['profile_visibility_choices']

        # Should be a list
        self.assertIsInstance(profile_choices, list)

        # Should have at least one choice
        self.assertGreater(len(profile_choices), 0)

        # Each choice should have 'value' and 'label' keys
        for choice in profile_choices:
            self.assertIn('value', choice)
            self.assertIn('label', choice)
            self.assertIsInstance(choice['value'], str)
            self.assertIsInstance(choice['label'], str)

    def test_expected_search_visibility_choices(self):
        """Test that expected search visibility choices are present."""
        response = self.client.get(self.choices_url)

        search_choices = response.data['search_visibility_choices']
        choice_values = [choice['value'] for choice in search_choices]

        # Based on your models.py SEARCH_VISIBILITY_CHOICES
        expected_values = ['everyone', 'friends_of_friends', 'friends_only', 'nobody']

        for expected_value in expected_values:
            self.assertIn(expected_value, choice_values)

    def test_expected_profile_visibility_choices(self):
        """Test that expected profile visibility choices are present."""
        response = self.client.get(self.choices_url)

        profile_choices = response.data['profile_visibility_choices']
        choice_values = [choice['value'] for choice in profile_choices]

        # Based on your models.py PROFILE_VISIBILITY_CHOICES
        expected_values = ['public', 'friends_only', 'private']

        for expected_value in expected_values:
            self.assertIn(expected_value, choice_values)

    def test_choice_labels_are_human_readable(self):
        """Test that choice labels are human-readable (not just the value)."""
        response = self.client.get(self.choices_url)

        # Check search visibility choices
        search_choices = response.data['search_visibility_choices']
        for choice in search_choices:
            # Label should be different from value (more human-readable)
            # and should be title case or properly formatted
            self.assertNotEqual(choice['value'], choice['label'])
            self.assertTrue(choice['label'][0].isupper())  # Should start with capital

        # Check profile visibility choices
        profile_choices = response.data['profile_visibility_choices']
        for choice in profile_choices:
            self.assertNotEqual(choice['value'], choice['label'])
            self.assertTrue(choice['label'][0].isupper())  # Should start with capital

    def test_response_is_consistent(self):
        """Test that multiple requests return consistent data."""
        response1 = self.client.get(self.choices_url)
        response2 = self.client.get(self.choices_url)

        self.assertEqual(response1.data, response2.data)

    def test_only_get_method_allowed(self):
        """Test that only GET method is allowed."""
        # Test POST
        response = self.client.post(self.choices_url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Test PUT
        response = self.client.put(self.choices_url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Test PATCH
        response = self.client.patch(self.choices_url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Test DELETE
        response = self.client.delete(self.choices_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_specific_choice_values_and_labels(self):
        """Test specific expected choice values and labels."""
        response = self.client.get(self.choices_url)

        # Create lookup dictionaries for easier testing
        search_choices_dict = {
            choice['value']: choice['label']
            for choice in response.data['search_visibility_choices']
        }

        profile_choices_dict = {
            choice['value']: choice['label']
            for choice in response.data['profile_visibility_choices']
        }

        # Test specific search visibility mappings
        expected_search_mappings = {
            'everyone': 'Everyone',
            'friends_of_friends': 'Friends of Friends',
            'friends_only': 'Friends Only',
            'nobody': 'Nobody'
        }

        for value, expected_label in expected_search_mappings.items():
            self.assertIn(value, search_choices_dict)
            self.assertEqual(search_choices_dict[value], expected_label)

        # Test specific profile visibility mappings
        expected_profile_mappings = {
            'public': 'Public',
            'friends_only': 'Friends Only',
            'private': 'Private'
        }

        for value, expected_label in expected_profile_mappings.items():
            self.assertIn(value, profile_choices_dict)
            self.assertEqual(profile_choices_dict[value], expected_label)

    def test_choices_data_structure(self):
        """Test the overall structure of the choices response."""
        response = self.client.get(self.choices_url)

        # Should have exactly 2 top-level keys
        self.assertEqual(len(response.data.keys()), 2)

        # Test structure matches expected format
        expected_structure = {
            'search_visibility_choices': list,
            'profile_visibility_choices': list
        }

        for key, expected_type in expected_structure.items():
            self.assertIn(key, response.data)
            self.assertIsInstance(response.data[key], expected_type)
