from unittest import mock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings # To access BLOCKED_EMAIL_DOMAINS for testing
from rest_framework.test import APIRequestFactory, APITestCase # For providing request context if needed
from rest_framework import serializers # For ValidationError

from ..models import UserProfile
from ..serializers import ProfileSerializer, UserSerializer, UserRegistrationSerializer
# Import your choices if needed for creating valid test data
from ..models_choices import OCCUPATION_CHOICES, COUNTRY_CHOICES, LANGUAGE_CHOICES

User = get_user_model()

class TestProfileSerializer(APITestCase): # Or APITestCase if you need request context for hyperlinking

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='profileuser', password='password123', email='profile@example.com')
        # UserProfile is auto-created by signal
        cls.profile = cls.user.userprofile
        cls.profile.bio = "Test bio"
        cls.profile.occupation = OCCUPATION_CHOICES[0][0]
        cls.profile.country = COUNTRY_CHOICES[0][0]
        # Add a friend for testing ManyToManyField serialization
        cls.friend_user = User.objects.create_user(username='friend', password='password123')
        cls.profile.friends.add(cls.friend_user)
        cls.profile.save()

        # For HyperlinkedModelSerializer, a request context is needed
        cls.factory = APIRequestFactory()
        cls.request = cls.factory.get('/') # Dummy request


    def test_profile_serialization(self):
        """Test ProfileSerializer output."""
        serializer = ProfileSerializer(self.profile, context={'request': self.request})
        data = serializer.data
        # print(data) # Helpful for debugging expected output

        self.assertIn('url', data) # Assuming HyperlinkedModelSerializer
        self.assertEqual(data['bio'], self.profile.bio)
        self.assertEqual(data['occupation'], self.profile.occupation)
        self.assertEqual(data['country'], self.profile.country)
        self.assertIn('picture', data) # Will be None or URL string
        self.assertIn('friends', data) # Will be a list of URLs or PKs
        self.assertTrue(len(data['friends']) >= 1)
        # Add more assertions for other fields like language


class TestUserSerializer(TestCase): # Or APITestCase

    @classmethod
    def setUpTestData(cls):
        cls.user_with_profile = User.objects.create_user(
            username='userwithprofile', password='password123', email='user@example.com'
        )
        # Profile should be auto-created
        cls.user_with_profile.userprofile.bio = "A detailed bio."
        cls.user_with_profile.userprofile.occupation = OCCUPATION_CHOICES[1][0]
        cls.user_with_profile.userprofile.save()

        cls.factory = APIRequestFactory()
        cls.request = cls.factory.get('/')

    def test_user_serialization_includes_profile(self):
        """Test UserSerializer includes nested profile data."""
        serializer = UserSerializer(self.user_with_profile, context={'request': self.request})
        data = serializer.data
        # print(data)

        self.assertEqual(data['username'], self.user_with_profile.username)
        self.assertIn('userprofile', data)
        self.assertIsNotNone(data['userprofile'])
        self.assertEqual(data['userprofile']['bio'], "A detailed bio.")
        self.assertEqual(data['userprofile']['occupation'], OCCUPATION_CHOICES[1][0])
        # Add assertions for other User fields like url, email, groups


class TestUserRegistrationSerializer(TestCase):

    def setUp(self):
        # It's good to have a clean slate for each registration test
        # especially for email/username uniqueness checks.
        # You can also define BLOCKED_EMAIL_DOMAINS in test settings if needed.
        self.valid_data = {
            'username': 'newuser',
            'email': 'newuser@domain.com',
            'password': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
            'first_name': 'New',
            'last_name': 'User'
        }

    def test_successful_registration(self):
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, self.valid_data['username'])
        self.assertEqual(user.email, self.valid_data['email'])
        self.assertTrue(user.check_password(self.valid_data['password']))
        self.assertTrue(user.is_active) # As per your create method
        # Check if profile was auto-created (requires signal to be connected during tests)
        self.assertTrue(hasattr(user, 'userprofile'))
        self.assertIsInstance(user.userprofile, UserProfile)


    def test_password_mismatch(self):
        data = self.valid_data.copy()
        data['password2'] = 'DifferentPassword123!'
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password2', serializer.errors)
        self.assertEqual(str(serializer.errors['password2'][0]), "Password fields didn't match.")

    def test_weak_password(self):
        data = self.valid_data.copy()
        data['password'] = 'weak'
        data['password2'] = 'weak'
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors) # Django's validators will populate this

    def test_existing_username(self):
        User.objects.create_user(username='newuser', password='password123')
        data = self.valid_data.copy() # username is 'newuser'
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
        self.assertEqual(str(serializer.errors['username'][0]), "A user with that username already exists.")

    def test_existing_email(self):
        User.objects.create_user(username='anotheruser', password='password123', email='newuser@domain.com')
        data = self.valid_data.copy() # email is 'newuser@domain.com'
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        self.assertEqual(str(serializer.errors['email'][0]), "A user with this email address already exists.")

    @mock.patch.object(settings, 'BLOCKED_EMAIL_DOMAINS', ['blocked.com']) # Temporarily mock settings
    def test_blocked_email_domain(self):
        # If settings are not easily mockable or you prefer not to,
        # you might need to set up test-specific settings.
        # For now, assuming we can mock or settings are picked up.
        # If BLOCKED_EMAIL_DOMAINS is always ['example.com', 'test.com'] from settings,
        # you can just test with one of those directly.
        # settings.BLOCKED_EMAIL_DOMAINS = ['blocked.com'] # This might not work reliably in all test runners
                                                       # without proper settings override.
                                                       # Using @mock.patch is better.

        data = self.valid_data.copy()
        data['email'] = 'user@blocked.com'
        serializer = UserRegistrationSerializer(data=data)

        # Ensure settings are configured for tests if you're directly accessing them in the serializer
        # This is a common gotcha. The serializer's validate_email accesses settings.BLOCKED_EMAIL_DOMAINS
        # Make sure this setting is available and has a value during tests.
        # If not using @mock.patch, you'd typically define it in a test settings file or override_settings
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        self.assertEqual(str(serializer.errors['email'][0]), "Registration from this email domain is not allowed.")

    # Add tests for missing required fields (username, email, password, password2)
    def test_missing_required_fields(self):
        required_fields = ['username', 'email', 'password', 'password2']
        for field_to_remove in required_fields:
            data = self.valid_data.copy()
            data.pop(field_to_remove)
            serializer = UserRegistrationSerializer(data=data)
            self.assertFalse(serializer.is_valid(), f"Validation should fail when {field_to_remove} is missing.")
            self.assertIn(field_to_remove, serializer.errors, f"{field_to_remove} should be in errors.")