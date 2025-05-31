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
        """Test ProfileSerializer output, including website_url."""
        self.profile.website_url = "https://example.com/profileuser"
        self.profile.save()
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
        self.assertIn('website_url', data)
        self.assertEqual(data['website_url'], "https://example.com/profileuser")
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
        self.assertIn('profile_url', data)
        # Add assertions for other User fields like url, email, groups