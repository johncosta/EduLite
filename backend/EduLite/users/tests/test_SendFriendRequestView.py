import sys
from pathlib import Path

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status

# Add performance testing framework to path
backend_path = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

from performance_testing.python_bindings.django_integration_mercury import DjangoMercuryAPITestCase
from performance_testing.python_bindings.monitor import monitor_django_view, monitor_serializer
from ..models import UserProfile, ProfileFriendRequest

User = get_user_model()


class SendFriendRequestViewMercuryTests(DjangoMercuryAPITestCase):
    """
    Mercury Performance Test Suite for SendFriendRequestView
    
    Monitors performance of friend request creation with focus on:
    - Request validation and serialization performance
    - Notification generation efficiency  
    - Database constraint checking (duplicate requests, existing friends)
    - Memory usage during request creation and validation
    - Serializer performance analysis
    """

    @classmethod
    def setUpClass(cls):
        """Configure Mercury with manual monitoring capabilities."""
        super().setUpClass()
        
        # Configure Mercury for detailed manual monitoring
        cls.configure_mercury(
            enabled=True,
            auto_scoring=True,
            auto_threshold_adjustment=True,
            store_history=True,                # Track request creation patterns over time
            generate_summaries=True,           # Executive insights on friend request performance
            verbose_reporting=False,           # Manual control over detailed output
            educational_guidance=True          # Learn optimization patterns for validations
        )
        
        # Set performance thresholds for friend request creation
        cls.set_performance_thresholds({
            'response_time_ms': 250,           # Allow time for validation queries
            'query_count_max': 18,             # Validation queries + notification creation
            'memory_overhead_mb': 35,          # Account for validation data structures
        })

    @classmethod
    def setUpTestData(cls):
        cls.user_sender = User.objects.create_user(
            username="sender", password="password123"
        )
        cls.profile_sender = UserProfile.objects.get(
            user=cls.user_sender
        )  # Assuming signal creates profile

        cls.user_receiver = User.objects.create_user(
            username="receiver", password="password123"
        )
        cls.profile_receiver = UserProfile.objects.get(user=cls.user_receiver)

        cls.user_already_friend = User.objects.create_user(
            username="already_friend", password="password123"
        )
        cls.profile_already_friend = UserProfile.objects.get(
            user=cls.user_already_friend
        )

        cls.send_request_url = reverse(
            "friend-request-send"
        )  # Ensure this name matches your urls.py

    def setUp(self):
        self.client.force_authenticate(user=self.user_sender)

    def test_send_friend_request_performance_analysis(self):
        """
        Test friend request creation with manual performance monitoring.
        
        Uses Mercury's manual monitoring to analyze:
        - Request validation query patterns
        - Serializer performance for request creation
        - Notification generation overhead
        - Memory efficiency during validation checks
        """
        data = {"receiver_profile_id": self.profile_receiver.pk}
        
        # Use manual monitoring for detailed performance insights
        with monitor_django_view("friend_request_creation") as monitor:
            response = self.client.post(self.send_request_url, data, format="json")
        
        # Standard functionality verification
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            ProfileFriendRequest.objects.filter(
                sender=self.profile_sender, receiver=self.profile_receiver
            ).exists()
        )
        self.assertIn("request_id", response.data)
        self.assertEqual(response.data["detail"], "Friend request sent successfully.")
        
        # Access detailed metrics from manual monitoring
        metrics = monitor.metrics
        
        # Detailed performance analysis with manual metrics access
        print(f"\\n🔍 Friend Request Creation Performance Analysis:")
        print(f"   📊 Response Time: {metrics.response_time:.2f}ms")
        print(f"   🗃️  Database Queries: {metrics.query_count}")
        print(f"   🧠 Memory Usage: {metrics.memory_usage:.2f}MB") 
        print(f"   🎯 Performance Grade: {metrics.performance_score.grade}")
        print(f"   ⚡ Status: {metrics.performance_status.value}")
        
        # Performance assertions using manual metrics
        self.assertLess(metrics.response_time, 200, 
                       f"Friend request creation took {metrics.response_time}ms - optimization needed")
        self.assertLess(metrics.query_count, 15, 
                       f"Used {metrics.query_count} queries - potential validation inefficiency")
        
        # Assert excellent performance for friend request creation
        self.assertPerformanceFast(metrics)
        self.assertMemoryEfficient(metrics)
        
        # Check detailed performance report
        detailed_report = metrics.get_performance_report_with_scoring()
        self.assertIsNotNone(detailed_report)

    def test_send_request_missing_receiver_id(self):
        response = self.client.post(self.send_request_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "receiver_profile_id is required.")

    def test_send_request_invalid_receiver_id(self):
        from rest_framework.exceptions import ErrorDetail

        data = {"receiver_profile_id": 99999}  # Non-existent PK
        response = self.client.post(self.send_request_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["detail"],
            ErrorDetail(
                string="No UserProfile matches the given query.", code="not_found"
            ),
        )

    def test_send_request_to_self(self):
        data = {"receiver_profile_id": self.profile_sender.pk}  # Sending to self
        response = self.client.post(self.send_request_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"], "You cannot send a friend request to yourself."
        )

    def test_send_request_to_existing_friend(self):
        # Make them friends first
        self.profile_sender.friends.add(self.profile_already_friend.user)

        data = {"receiver_profile_id": self.profile_already_friend.pk}
        response = self.client.post(self.send_request_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"], "You are already friends with this user."
        )

    def test_send_request_when_request_already_sent(self):
        # Send one request
        ProfileFriendRequest.objects.create(
            sender=self.profile_sender, receiver=self.profile_receiver
        )

        # Try to send again
        data = {"receiver_profile_id": self.profile_receiver.pk}
        response = self.client.post(self.send_request_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "You have already sent a friend request to this user.",
        )

    def test_send_request_when_request_already_received(self):
        # A request exists from receiver to sender
        ProfileFriendRequest.objects.create(
            sender=self.profile_receiver, receiver=self.profile_sender
        )

        # Sender tries to send to receiver
        data = {"receiver_profile_id": self.profile_receiver.pk}
        response = self.client.post(self.send_request_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "This user has already sent you a friend request. Check your pending requests.",
        )

    def test_send_request_with_invalid_receiver_id_type(self):
        """
        Test sending a request where receiver_profile_id is not a valid integer.
        """
        data = {"receiver_profile_id": "not-a-valid-integer"}
        response = self.client.post(self.send_request_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("detail"),
            "Invalid receiver_profile_id. Must be an integer.",
        )

    def test_validation_performance_with_serializer_monitoring(self):
        """
        Test validation performance using Mercury's serializer monitoring.
        
        Focuses on performance of various validation scenarios:
        - Self-request validation
        - Existing friend validation  
        - Duplicate request validation
        """
        # Test self-request validation performance
        with monitor_serializer("self_request_validation") as monitor:
            data = {"receiver_profile_id": self.profile_sender.pk}
            response = self.client.post(self.send_request_url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "You cannot send a friend request to yourself.")
        
        # Analyze validation performance
        validation_metrics = monitor.metrics
        self.assertLess(validation_metrics.response_time, 100, 
                       "Self-validation should be very fast")
        
        # Test existing friend validation performance
        self.profile_sender.friends.add(self.profile_already_friend.user)
        
        with monitor_django_view("existing_friend_validation") as monitor:
            data = {"receiver_profile_id": self.profile_already_friend.pk}
            response = self.client.post(self.send_request_url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "You are already friends with this user.")
        
        # Analyze friend check performance
        friend_check_metrics = monitor.metrics
        self.assertLess(friend_check_metrics.query_count, 8, 
                       "Friend existence check should be efficient")

    def test_bulk_request_creation_performance(self):
        """
        Test performance of creating multiple friend requests with comprehensive analysis.
        """
        # Create multiple potential recipients
        recipients = []
        for i in range(3):
            user = User.objects.create_user(
                username=f"recipient_{i}", password="password123"
            )
            profile = UserProfile.objects.get(user=user)
            recipients.append(profile)
        
        # Monitor bulk request creation
        metrics = self.run_comprehensive_analysis(
            operation_name="BulkFriendRequestCreation",
            test_function=lambda: self._create_multiple_requests(recipients),
            operation_type="create_view",
            expect_response_under=600,      # Allow more time for bulk operations
            expect_queries_under=40,        # Multiple validations + creations
            expect_memory_under=150,        # Bulk data handling
            print_analysis=False,
            show_scoring=True,
            auto_detect_n_plus_one=True     # Check for N+1 in bulk operations
        )
        
        # Verify all requests were created
        for recipient in recipients:
            self.assertTrue(
                ProfileFriendRequest.objects.filter(
                    sender=self.profile_sender, receiver=recipient
                ).exists(),
                f"Request to {recipient.user.username} not created"
            )
        
        # Assert production-ready performance for bulk operations
        self.assert_mercury_performance_production_ready(metrics)

    def _create_multiple_requests(self, recipients):
        """Helper method to create multiple friend requests."""
        responses = []
        for recipient in recipients:
            data = {"receiver_profile_id": recipient.pk}
            response = self.client.post(self.send_request_url, data, format="json")
            responses.append(response)
            # Verify each request succeeds
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return responses

    def test_performance_under_different_thresholds(self):
        """
        Test with custom per-test thresholds for different scenarios.
        """
        # Test with strict thresholds for simple request creation
        self.set_test_performance_thresholds({
            'response_time_ms': 150,     # Strict timing for single request
            'query_count_max': 12,       # Minimal validation queries
            'memory_overhead_mb': 25,    # Efficient memory usage
        })
        
        data = {"receiver_profile_id": self.profile_receiver.pk}
        response = self.client.post(self.send_request_url, data, format="json")
        
        # Mercury automatically applies custom thresholds
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"], "Friend request sent successfully.")
