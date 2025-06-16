# users/tests/functions/test_delete_notification_on_friend_request.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

from ...models import UserProfile, ProfileFriendRequest
from ...signals import delete_notification_on_friend_request

User = get_user_model()


class DeleteNotificationOnFriendRequestTests(TestCase):
    """
    Test suite for the delete_notification_on_friend_request signal handler.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data that will be used across multiple test methods.
        """
        # Create test users
        cls.sender_user = User.objects.create_user(
            username="sender", password="password123"
        )
        cls.receiver_user = User.objects.create_user(
            username="receiver", password="password123"
        )

        # Get their profiles (created automatically by signals)
        cls.sender_profile = UserProfile.objects.get(user=cls.sender_user)
        cls.receiver_profile = UserProfile.objects.get(user=cls.receiver_user)

    @patch("notifications.models.Notification")
    @patch("django.contrib.contenttypes.models.ContentType")
    def test_deletes_notification_on_friend_request_deletion(self, mock_content_type_model, mock_notification_model):
        """
        Test that the signal handler deletes the notification when a friend request is deleted.
        """
        # --- Setup Mock ---
        mock_content_type = MagicMock()
        mock_content_type_model.objects.get_for_model.return_value = mock_content_type
        mock_notification_instance = MagicMock()
        mock_notification_model.objects.get.return_value = mock_notification_instance

        # --- Action ---
        # Create a friend request
        friend_request = ProfileFriendRequest.objects.create(
            sender=self.sender_profile,
            receiver=self.receiver_profile
        )
        friend_request_id = friend_request.id

        # Delete the friend request, which should trigger the signal
        friend_request.delete()

        # --- Assertions ---
        # Verify that ContentType was fetched
        mock_content_type_model.objects.get_for_model.assert_called_once_with(ProfileFriendRequest)

        # Verify that the notification was looked up using ContentType and object_id
        mock_notification_model.objects.get.assert_called_once_with(
            target_content_type=mock_content_type,
            target_object_id=friend_request_id
        )

        # Verify that the notification was deleted
        mock_notification_instance.delete.assert_called_once()

    @patch("notifications.models.Notification")
    @patch("django.contrib.contenttypes.models.ContentType")
    def test_handles_notification_not_found_gracefully(self, mock_content_type_model, mock_notification_model):
        """
        Test that the signal handler handles cases where no notification exists for the friend request.
        """
        # --- Setup Mock ---
        mock_content_type = MagicMock()
        mock_content_type_model.objects.get_for_model.return_value = mock_content_type

        # Make the notification lookup raise DoesNotExist
        from notifications.models import Notification
        mock_notification_model.objects.get.side_effect = Notification.DoesNotExist()

        # --- Action ---
        friend_request = ProfileFriendRequest.objects.create(
            sender=self.sender_profile,
            receiver=self.receiver_profile
        )
        friend_request_id = friend_request.id

        # Delete the friend request - should not raise an exception
        try:
            friend_request.delete()
        except Exception as e:
            self.fail(f"Signal handler should handle DoesNotExist gracefully, but raised: {e}")

        # --- Assertions ---
        # Verify that the notification lookup was attempted with ContentType
        mock_notification_model.objects.get.assert_called_once_with(
            target_content_type=mock_content_type,
            target_object_id=friend_request_id
        )


    @patch("users.signals.logger")
    @patch("notifications.models.Notification")
    def test_logs_successful_notification_deletion(self, mock_notification_model, mock_logger):
        """
        Test that the signal handler logs successful notification deletion in debug mode.
        """
        # --- Setup Mock ---
        mock_notification_instance = MagicMock()
        mock_notification_model.objects.get.return_value = mock_notification_instance
        mock_logger.isEnabledFor.return_value = True

        # Create the friend request first
        friend_request = ProfileFriendRequest.objects.create(
            sender=self.sender_profile,
            receiver=self.receiver_profile
        )

        # Store the ID before deletion since it might become None
        friend_request_id = friend_request.id

        # Reset the logger mock to clear creation logs
        mock_logger.reset_mock()
        mock_logger.isEnabledFor.return_value = True

        # --- Action ---
        # Delete the friend request (this will trigger deletion signal)
        friend_request.delete()

        # --- Assertions ---
        # Verify that debug logging was called for deletion
        mock_logger.debug.assert_called_once()

        # Verify the debug log contains the friend request ID
        debug_call_args = mock_logger.debug.call_args[0]
        self.assertIn("Deleted notification for friend request", debug_call_args[0])
        self.assertEqual(debug_call_args[1], friend_request_id)

    @patch("users.signals.logger")
    @patch("notifications.models.Notification")
    def test_logs_notification_not_found_in_debug_mode(self, mock_notification_model, mock_logger):
        """
        Test that the signal handler logs when no notification is found in debug mode.
        """
        # --- Setup Mock ---
        from django.core.exceptions import ObjectDoesNotExist
        mock_notification_model.objects.get.side_effect = ObjectDoesNotExist
        mock_logger.isEnabledFor.return_value = True

        # Create the friend request first
        friend_request = ProfileFriendRequest.objects.create(
            sender=self.sender_profile,
            receiver=self.receiver_profile
        )

        # Store the ID before deletion
        friend_request_id = friend_request.id

        # Reset the logger mock to clear creation logs
        mock_logger.reset_mock()
        mock_logger.isEnabledFor.return_value = True

        # --- Action ---
        friend_request.delete()

        # --- Assertions ---
        # Verify that debug logging was called for the "not found" case
        mock_logger.debug.assert_called_once()

        # Verify the debug log indicates no notification was found
        debug_call_args = mock_logger.debug.call_args[0]
        self.assertIn("No notification found for friend request", debug_call_args[0])
        self.assertEqual(debug_call_args[1], friend_request_id)

    @patch("users.signals.logger")
    @patch("notifications.models.Notification")
    def test_logs_deletion_failure_errors(self, mock_notification_model, mock_logger):
        """
        Test that the signal handler logs errors when notification deletion fails.
        """
        # --- Setup Mock ---
        mock_notification_instance = MagicMock()
        mock_notification_model.objects.get.return_value = mock_notification_instance
        # Make the delete operation raise an exception
        mock_notification_instance.delete.side_effect = Exception("Database error")

        # Create the friend request first
        friend_request = ProfileFriendRequest.objects.create(
            sender=self.sender_profile,
            receiver=self.receiver_profile
        )

        # Store the ID before deletion
        friend_request_id = friend_request.id

        # Reset the logger mock to clear creation logs
        mock_logger.reset_mock()

        # --- Action ---
        friend_request.delete()

        # --- Assertions ---
        # Verify that error logging was called
        mock_logger.error.assert_called_once()

        # Verify the error log contains relevant information
        error_call_args = mock_logger.error.call_args[0]
        self.assertIn("Failed to delete notification for friend request", error_call_args[0])
        self.assertEqual(error_call_args[1], friend_request_id)        # friend request ID
        self.assertIn("Database error", str(error_call_args[2]))       # Exception message

    @patch("notifications.models.Notification")
    @patch("django.contrib.contenttypes.models.ContentType")
    def test_uses_content_type_lookup_for_deleted_objects(self, mock_content_type_model, mock_notification_model):
        """
        Test that the signal handler uses ContentType lookup instead of target lookup for deleted objects.
        """
        # --- Setup Mock ---
        mock_content_type = MagicMock()
        mock_content_type_model.objects.get_for_model.return_value = mock_content_type
        mock_notification_instance = MagicMock()
        mock_notification_model.objects.get.return_value = mock_notification_instance

        # --- Action ---
        friend_request = ProfileFriendRequest.objects.create(
            sender=self.sender_profile,
            receiver=self.receiver_profile
        )
        friend_request_id = friend_request.id
        friend_request.delete()

        # --- Assertions ---
        # Verify ContentType was obtained for ProfileFriendRequest
        mock_content_type_model.objects.get_for_model.assert_called_once_with(ProfileFriendRequest)

        # Verify notification was looked up by content_type and object_id
        mock_notification_model.objects.get.assert_called_once_with(
            target_content_type=mock_content_type,
            target_object_id=friend_request_id
        )

        # Verify notification was deleted
        mock_notification_instance.delete.assert_called_once()


    def test_signal_handler_function_exists_and_is_callable(self):
        """
        Test that the delete signal handler function exists and can be called directly.
        """
        # --- Assertions ---
        # Verify the function exists
        self.assertTrue(callable(delete_notification_on_friend_request))

        # Verify the function has the expected parameters
        import inspect
        sig = inspect.signature(delete_notification_on_friend_request)
        expected_params = ['sender', 'instance']

        # Check that all expected parameters are present (kwargs is also expected)
        actual_params = list(sig.parameters.keys())
        for param in expected_params:
            self.assertIn(param, actual_params)

    @patch("notifications.models.Notification")
    def test_handles_none_instance_gracefully(self, mock_notification_model):
        """
        Test that the signal handler handles None instance gracefully.
        """
        # --- Action & Assertions ---
        # Call the signal handler directly with None instance
        try:
            delete_notification_on_friend_request(
                sender=ProfileFriendRequest,
                instance=None
            )
        except Exception as e:
            self.fail(f"Signal handler should handle None instance gracefully, but raised: {e}")

        # --- Assertions ---
        # Verify that no notification lookup was attempted
        mock_notification_model.objects.get.assert_not_called()

    @patch("users.signals.logger")
    @patch("notifications.models.Notification")
    def test_logs_warning_for_none_instance(self, mock_notification_model, mock_logger):
        """
        Test that the signal handler logs a warning when instance is None.
        """
        # --- Action ---
        delete_notification_on_friend_request(
            sender=ProfileFriendRequest,
            instance=None
        )

        # --- Assertions ---
        # Verify that warning logging was called
        mock_logger.warning.assert_called_once_with(
            "ProfileFriendRequest instance is None in delete signal"
        )

    @patch("notifications.models.Notification")
    @patch("django.contrib.contenttypes.models.ContentType")
    def test_uses_getattr_for_safe_id_access(self, mock_content_type_model, mock_notification_model):
        """
        Test that the signal handler safely accesses the instance ID using getattr.
        """
        # --- Setup Mock ---
        mock_content_type = MagicMock()
        mock_content_type_model.objects.get_for_model.return_value = mock_content_type

        # Create a mock instance without an 'id' attribute but with 'pk'
        mock_instance = MagicMock()
        if hasattr(mock_instance, 'id'):
            del mock_instance.id
        mock_instance.pk = 'test_pk'

        from notifications.models import Notification
        mock_notification_model.objects.get.side_effect = Notification.DoesNotExist()

        # --- Action ---
        # Should not raise AttributeError even without 'id' attribute
        try:
            delete_notification_on_friend_request(
                sender=ProfileFriendRequest,
                instance=mock_instance
            )
        except AttributeError as e:
            self.fail(f"Signal handler should safely access ID using getattr, but raised: {e}")

        # --- Assertions ---
        # Verify that the notification lookup was attempted with the pk value
        mock_notification_model.objects.get.assert_called_once_with(
            target_content_type=mock_content_type,
            target_object_id='test_pk'
        )
