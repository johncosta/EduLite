from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError # For testing unique constraints

from users.models import UserProfile, ProfileFriendRequest 

User = get_user_model()

class ProfileFriendRequestModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create users
        cls.user1 = User.objects.create_user(username='user1', password='password123')
        cls.user2 = User.objects.create_user(username='user2', password='password123')
        cls.user3 = User.objects.create_user(username='user3', password='password123')
        # Signals will create UserProfile instances for each User
        cls.profile1 = UserProfile.objects.get(user=cls.user1)
        cls.profile2 = UserProfile.objects.get(user=cls.user2)
        cls.profile3 = UserProfile.objects.get(user=cls.user3)

    def test_create_friend_request(self):
        """Test that a ProfileFriendRequest can be created successfully."""
        request = ProfileFriendRequest.objects.create(sender=self.profile1, receiver=self.profile2)
        self.assertIsNotNone(request.pk)
        self.assertIsNotNone(request.created_at)
        self.assertEqual(str(request), f"Friend request from {self.profile1.user.username} to {self.profile2.user.username}")

    def test_unique_pending_friend_request_constraint(self):
        """Test the unique constraint for (sender, receiver)."""
        ProfileFriendRequest.objects.create(sender=self.profile1, receiver=self.profile2)
        with self.assertRaises(IntegrityError): # Or the specific exception your DB raises
            ProfileFriendRequest.objects.create(sender=self.profile1, receiver=self.profile2)

    def test_clean_method_prevents_self_request(self):
        """Test that a user cannot send a friend request to themselves."""
        request_to_self = ProfileFriendRequest(sender=self.profile1, receiver=self.profile1)
        with self.assertRaisesMessage(ValidationError, "Cannot send a friend request to oneself."):
            request_to_self.full_clean() # full_clean() calls clean()

    def test_accept_friend_request(self):
        """Test the accept() method."""
        friend_request = ProfileFriendRequest.objects.create(sender=self.profile1, receiver=self.profile2)
        
        # Ensure they are not friends initially
        self.assertNotIn(self.profile1.user, self.profile2.friends.all())
        self.assertNotIn(self.profile2.user, self.profile1.friends.all())

        result = friend_request.accept()
        self.assertTrue(result)

        # Verify they are now friends
        self.profile1.refresh_from_db() # Refresh to get updated friends list
        self.profile2.refresh_from_db()
        self.assertIn(self.profile1.user, self.profile2.friends.all())
        self.assertIn(self.profile2.user, self.profile1.friends.all())

        # Verify the request object is deleted
        with self.assertRaises(ProfileFriendRequest.DoesNotExist):
            ProfileFriendRequest.objects.get(pk=friend_request.pk)

    def test_decline_friend_request(self):
        """Test the decline() method."""
        friend_request = ProfileFriendRequest.objects.create(sender=self.profile1, receiver=self.profile2)
        request_pk = friend_request.pk # Get pk before deleting

        result = friend_request.decline()
        self.assertTrue(result)

        # Verify the request object is deleted
        with self.assertRaises(ProfileFriendRequest.DoesNotExist):
            ProfileFriendRequest.objects.get(pk=request_pk)
        
        # Verify they are not friends
        self.assertNotIn(self.profile1.user, self.profile2.friends.all())
        self.assertNotIn(self.profile2.user, self.profile1.friends.all())

    def test_accept_idempotency_or_failure_if_already_accepted(self):
        """
        Test behavior if accept is called on a deleted request (it won't exist).
        This also implicitly tests that once accepted, the request is gone.
        """
        friend_request = ProfileFriendRequest.objects.create(sender=self.profile1, receiver=self.profile2)
        friend_request_id = friend_request.id
        friend_request.accept()

        # Now try to get and accept again (should fail as it's deleted)
        with self.assertRaises(ProfileFriendRequest.DoesNotExist):
            deleted_request = ProfileFriendRequest.objects.get(id=friend_request_id)

