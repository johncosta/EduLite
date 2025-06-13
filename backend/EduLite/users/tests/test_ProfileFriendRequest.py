from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError  # For testing unique constraints

from users.models import UserProfile, ProfileFriendRequest

User = get_user_model()


class ProfileFriendRequestModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create users
        cls.user1 = User.objects.create_user(username="user1", password="password123")
        cls.user2 = User.objects.create_user(username="user2", password="password123")
        cls.user3 = User.objects.create_user(username="user3", password="password123")
        # Signals will create UserProfile instances for each User
        cls.profile1 = UserProfile.objects.get(user=cls.user1)
        cls.profile2 = UserProfile.objects.get(user=cls.user2)
        cls.profile3 = UserProfile.objects.get(user=cls.user3)

    def test_create_friend_request(self):
        """Test that a ProfileFriendRequest can be created successfully."""
        request = ProfileFriendRequest.objects.create(
            sender=self.profile1, receiver=self.profile2
        )
        self.assertIsNotNone(request.pk)
        self.assertIsNotNone(request.created_at)
        self.assertEqual(
            str(request),
            f"Friend request from {self.profile1.user.username} to {self.profile2.user.username}",
        )

    def test_unique_pending_friend_request_constraint(self):
        """Test the unique constraint for (sender, receiver)."""
        ProfileFriendRequest.objects.create(
            sender=self.profile1, receiver=self.profile2
        )
        with self.assertRaises(
            IntegrityError
        ):  # Or the specific exception your DB raises
            ProfileFriendRequest.objects.create(
                sender=self.profile1, receiver=self.profile2
            )

    def test_clean_method_prevents_self_request(self):
        """Test that a user cannot send a friend request to themselves."""
        request_to_self = ProfileFriendRequest(
            sender=self.profile1, receiver=self.profile1
        )
        with self.assertRaisesMessage(
            ValidationError, "Cannot send a friend request to oneself."
        ):
            request_to_self.full_clean()  # full_clean() calls clean()

    def test_accept_friend_request(self):
        """Test the accept() method."""
        friend_request = ProfileFriendRequest.objects.create(
            sender=self.profile1, receiver=self.profile2
        )

        # Ensure they are not friends initially
        self.assertNotIn(self.profile1.user, self.profile2.friends.all())
        self.assertNotIn(self.profile2.user, self.profile1.friends.all())

        result = friend_request.accept()
        self.assertTrue(result)

        # Verify they are now friends
        self.profile1.refresh_from_db()  # Refresh to get updated friends list
        self.profile2.refresh_from_db()
        self.assertIn(self.profile1.user, self.profile2.friends.all())
        self.assertIn(self.profile2.user, self.profile1.friends.all())

        # Verify the request object is deleted
        with self.assertRaises(ProfileFriendRequest.DoesNotExist):
            ProfileFriendRequest.objects.get(pk=friend_request.pk)

    def test_decline_friend_request(self):
        """Test the decline() method."""
        friend_request = ProfileFriendRequest.objects.create(
            sender=self.profile1, receiver=self.profile2
        )
        request_pk = friend_request.pk  # Get pk before deleting

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
        friend_request = ProfileFriendRequest.objects.create(
            sender=self.profile1, receiver=self.profile2
        )
        friend_request_id = friend_request.id
        friend_request.accept()

        # Now try to get and accept again (should fail as it's deleted)
        with self.assertRaises(ProfileFriendRequest.DoesNotExist):
            deleted_request = ProfileFriendRequest.objects.get(id=friend_request_id)

    def test_clean_method_prevents_request_if_already_friends(self):
        """
        Test that a ValidationError is raised if a friend request is sent
        to someone who is already a friend.
        """
        # Make user1 (via profile1) and user2 friends
        self.profile1.friends.add(self.user2)
        self.user2.profile.friends.add(self.user1)
        # Verifying the friendship for clarity in the test
        self.assertTrue(self.profile1.friends.filter(pk=self.user2.pk).exists())
        self.assertTrue(
            self.user2.profile.friends.filter(pk=self.profile1.pk).exists()
        )  # Check reverse via related_name

        # Attempt to create a friend request from profile1 to profile2
        request_to_friend = ProfileFriendRequest(
            sender=self.profile1, receiver=self.profile2
        )
        with self.assertRaisesMessage(
            ValidationError, "Cannot send a friend request to a friend."
        ):
            request_to_friend.full_clean()

        # Test the other direction as well (profile2 trying to send to profile1)
        request_from_friend = ProfileFriendRequest(
            sender=self.profile2, receiver=self.profile1
        )
        with self.assertRaisesMessage(
            ValidationError, "Cannot send a friend request to a friend."
        ):
            request_from_friend.full_clean()

    def test_clean_method_allows_request_if_not_friends(self):
        """
        Test that a friend request can be made if users are not friends.
        This is a sanity check to ensure the previous test isn't overly restrictive.
        """
        # Ensure profile1 and profile3 are NOT friends initially
        self.assertFalse(self.profile1.friends.filter(pk=self.user3.pk).exists())

        # Attempt to create a friend request from profile1 to profile3
        request_to_non_friend = ProfileFriendRequest(
            sender=self.profile1, receiver=self.profile3
        )
        try:
            request_to_non_friend.full_clean()  # Should not raise ValidationError for this specific check
        except ValidationError as e:
            # Check if the error is specifically "Cannot send a friend request to a friend."
            # If it is, then this test fails. Any other validation error is fine for this test's scope.
            if "Cannot send a friend request to a friend." in str(e):
                self.fail("ValidationError was raised for non-friends: " + str(e))


class UserProfileFriendRequestInteractionTests(
    TestCase
):  # Or APITestCase if making API calls later
    @classmethod
    def setUpTestData(cls):
        # Users
        cls.user_sender = User.objects.create_user(
            username="sender_user", password="password123"
        )
        cls.user_receiver1 = User.objects.create_user(
            username="receiver1_user", password="password123"
        )
        cls.user_receiver2 = User.objects.create_user(
            username="receiver2_user", password="password123"
        )
        cls.user_another_sender = User.objects.create_user(
            username="another_sender", password="password123"
        )

        # Profiles (assuming signals create them)
        cls.profile_sender = UserProfile.objects.get(user=cls.user_sender)
        cls.profile_receiver1 = UserProfile.objects.get(user=cls.user_receiver1)
        cls.profile_receiver2 = UserProfile.objects.get(user=cls.user_receiver2)
        cls.profile_another_sender = UserProfile.objects.get(
            user=cls.user_another_sender
        )

        # Create some friend requests
        # sender sends to receiver1 and receiver2
        ProfileFriendRequest.objects.create(
            sender=cls.profile_sender, receiver=cls.profile_receiver1
        )
        ProfileFriendRequest.objects.create(
            sender=cls.profile_sender, receiver=cls.profile_receiver2
        )

        # another_sender sends to receiver1
        ProfileFriendRequest.objects.create(
            sender=cls.profile_another_sender, receiver=cls.profile_receiver1
        )

    def test_get_sent_friend_requests_from_profile(self):
        """
        Test accessing sent friend requests via user_profile.sent_friend_requests.all().
        """
        sent_requests = self.profile_sender.sent_friend_requests.all()
        self.assertEqual(sent_requests.count(), 2)
        # Check that the receivers are correct
        receiver_pks = {req.receiver.pk for req in sent_requests}
        self.assertIn(self.profile_receiver1.pk, receiver_pks)
        self.assertIn(self.profile_receiver2.pk, receiver_pks)

        # Check for a user with no sent requests
        no_sent_requests = self.profile_receiver1.sent_friend_requests.all()
        self.assertEqual(no_sent_requests.count(), 0)

    def test_get_received_friend_requests_from_profile(self):
        """
        Test accessing received friend requests via user_profile.received_friend_requests.all().
        """
        received_by_receiver1 = self.profile_receiver1.received_friend_requests.all()
        self.assertEqual(received_by_receiver1.count(), 2)
        # Check that the senders are correct
        sender_pks = {req.sender.pk for req in received_by_receiver1}
        self.assertIn(self.profile_sender.pk, sender_pks)
        self.assertIn(self.profile_another_sender.pk, sender_pks)

        received_by_receiver2 = self.profile_receiver2.received_friend_requests.all()
        self.assertEqual(received_by_receiver2.count(), 1)
        self.assertEqual(received_by_receiver2.first().sender, self.profile_sender)

        # Check for a user with no received requests
        no_received_requests = self.profile_sender.received_friend_requests.all()
        self.assertEqual(no_received_requests.count(), 0)

    def test_filter_on_related_requests(self):
        """
        Test filtering on the related manager for friend requests.
        """
        # Example: Find requests received by profile_receiver1 from profile_sender
        specific_request_qs = self.profile_receiver1.received_friend_requests.filter(
            sender=self.profile_sender
        )
        self.assertEqual(specific_request_qs.count(), 1)
        self.assertEqual(specific_request_qs.first().sender, self.profile_sender)

        # Example: Check if profile_sender has sent a request to profile_receiver1
        has_sent_request = self.profile_sender.sent_friend_requests.filter(
            receiver=self.profile_receiver1
        ).exists()
        self.assertTrue(has_sent_request)

        has_sent_to_non_receiver = self.profile_sender.sent_friend_requests.filter(
            receiver=self.profile_another_sender
        ).exists()
        self.assertFalse(has_sent_to_non_receiver)

    def test_related_name_after_request_accepted(self):
        """
        Test how related names behave after a request is accepted (and thus deleted).
        """
        request_to_accept = self.profile_sender.sent_friend_requests.get(
            receiver=self.profile_receiver1
        )

        # Before accept
        self.assertEqual(self.profile_sender.sent_friend_requests.count(), 2)
        self.assertEqual(self.profile_receiver1.received_friend_requests.count(), 2)

        request_to_accept.accept()

        # After accept, the request is deleted, so it should not appear in these querysets
        self.assertEqual(
            self.profile_sender.sent_friend_requests.count(), 1
        )  # One less sent
        self.assertEqual(
            self.profile_receiver1.received_friend_requests.count(), 1
        )  # One less received

        # Verify they are friends
        self.assertTrue(
            self.profile_sender.friends.filter(pk=self.user_receiver1.pk).exists()
        )
        self.assertTrue(
            self.profile_receiver1.friends.filter(pk=self.user_sender.pk).exists()
        )

    def test_related_name_after_request_declined(self):
        """
        Test how related names behave after a request is declined (and thus deleted).
        """
        request_to_decline = self.profile_sender.sent_friend_requests.get(
            receiver=self.profile_receiver2
        )

        # Before decline
        self.assertEqual(
            self.profile_sender.sent_friend_requests.count(), 2
        )  # Assuming this test runs after setUpTestData
        # To make it isolated, re-fetch count based on initial setup or setup specific request for this test
        initial_sent_count_for_sender = ProfileFriendRequest.objects.filter(
            sender=self.profile_sender
        ).count()
        initial_received_count_for_receiver2 = ProfileFriendRequest.objects.filter(
            receiver=self.profile_receiver2
        ).count()

        self.assertEqual(initial_sent_count_for_sender, 2)
        self.assertEqual(initial_received_count_for_receiver2, 1)

        request_to_decline.decline()

        # After decline
        self.assertEqual(
            self.profile_sender.sent_friend_requests.count(),
            initial_sent_count_for_sender - 1,
        )
        self.assertEqual(
            self.profile_receiver2.received_friend_requests.count(),
            initial_received_count_for_receiver2 - 1,
        )

        # Verify they are NOT friends
        self.assertFalse(
            self.profile_sender.friends.filter(pk=self.user_receiver2.pk).exists()
        )
        self.assertFalse(
            self.profile_receiver2.friends.filter(pk=self.user_sender.pk).exists()
        )
