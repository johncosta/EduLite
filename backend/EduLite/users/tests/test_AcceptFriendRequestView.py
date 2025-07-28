import sys
from pathlib import Path

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status

# Add performance testing framework to path
backend_path = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

from performance_testing.python_bindings.django_integration_mercury import DjangoMercuryAPITestCase
from performance_testing.python_bindings.monitor import monitor_django_view
from ..models import UserProfile, ProfileFriendRequest
from ..permissions import IsFriendRequestReceiver

User = get_user_model()


class AcceptFriendRequestViewMercuryTests(DjangoMercuryAPITestCase):
    """
    Mercury Performance Test Suite for AcceptFriendRequestView
    
    Monitors performance of friend request acceptance operations with focus on:
    - Friendship establishment query patterns
    - Notification generation performance  
    - N+1 query detection in relationship updates
    - Database cascade operations efficiency
    - Memory usage during friendship creation
    """

    @classmethod
    def setUpClass(cls):
        """Configure Mercury for intelligent performance monitoring with advanced features."""
        super().setUpClass()
        
        # Configure comprehensive Mercury features
        cls.configure_mercury(
            enabled=True,
            auto_scoring=True,
            auto_threshold_adjustment=True,
            store_history=True,                # Enable historical tracking
            generate_summaries=True,           # Executive summaries  
            verbose_reporting=False,           # Detailed per-test reporting
            educational_guidance=True          # Learning optimization patterns
        )
        
        # Set intelligent thresholds for friend request operations
        cls.set_performance_thresholds({
            'response_time_ms': 200,           # Friend acceptance should be fast
            'query_count_max': 15,             # Allow for relationship updates + notifications
            'memory_overhead_mb': 30,          # Account for friendship data structures
        })

    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole test class."""
        # Create users and their profiles
        cls.user_sender = User.objects.create_user(
            username="sender_user", password="password123"
        )
        cls.profile_sender = UserProfile.objects.get(user=cls.user_sender)

        cls.user_receiver = User.objects.create_user(
            username="receiver_user", password="password123"
        )
        cls.profile_receiver = UserProfile.objects.get(user=cls.user_receiver)

        cls.user_unrelated = User.objects.create_user(
            username="unrelated_user", password="password123"
        )

        # Create a friend request from sender to receiver
        cls.friend_request = ProfileFriendRequest.objects.create(
            sender=cls.profile_sender, receiver=cls.profile_receiver
        )

        # Define the URL for the accept action
        cls.accept_url = reverse(
            "friend-request-accept", kwargs={"request_pk": cls.friend_request.pk}
        )

    def test_accept_request_unauthenticated(self):
        """
        Test that an unauthenticated user cannot accept a friend request.
        """
        response = self.client.post(self.accept_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_receiver_can_accept_request_performance(self):
        """
        Test friend request acceptance with comprehensive performance analysis.
        
        This is the critical path for friendship establishment - monitor for:
        - N+1 queries in friendship creation
        - Notification generation performance  
        - Database cascade operations
        - Memory efficiency during relationship updates
        """
        self.client.force_authenticate(user=self.user_receiver)
        
        # Use comprehensive analysis for critical friendship operation
        metrics = self.run_comprehensive_analysis(
            operation_name="FriendRequestAcceptance",
            test_function=lambda: self.client.post(self.accept_url),
            operation_type="create_view",  # Creates friendship relationship
            expect_response_under=150,      # Critical path should be fast
            expect_queries_under=12,        # Relationship updates + cleanup
            expect_memory_under=100,        # Efficient friendship creation
            print_analysis=False,           # Controlled output
            show_scoring=True,              # Show performance grade
            auto_detect_n_plus_one=True     # Critical for relationship queries
        )

        # Standard functionality verification
        response = metrics._test_result
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Friend request accepted.")

        # Verify database operations completed correctly
        with self.assertRaises(ProfileFriendRequest.DoesNotExist):
            ProfileFriendRequest.objects.get(pk=self.friend_request.pk)

        # Verify symmetric friendship establishment
        self.profile_sender.refresh_from_db()
        self.profile_receiver.refresh_from_db()
        self.assertIn(self.user_receiver, self.profile_sender.friends.all())
        self.assertIn(self.user_sender, self.profile_receiver.friends.all())
        
        # Assert production-ready performance for critical friendship operation
        self.assert_mercury_performance_production_ready(metrics)
        
        # Ensure no N+1 queries in relationship operations
        self.assertNoNPlusOne(metrics)
        
        # Verify memory efficiency for friendship data
        self.assertMemoryEfficient(metrics)

    def test_sender_cannot_accept_request(self):
        """
        Test that the sender of a request cannot accept it themselves.
        """
        # Authenticate as the sender
        self.client.force_authenticate(user=self.user_sender)
        response = self.client.post(self.accept_url)

        # This tests the IsFriendRequestReceiver permission
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unrelated_user_cannot_accept_request(self):
        """
        Test that a user who is not party to the request cannot accept it.
        """
        # Authenticate as the unrelated user
        self.client.force_authenticate(user=self.user_unrelated)
        response = self.client.post(self.accept_url)

        # This also tests the IsFriendRequestReceiver permission
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_accept_nonexistent_request(self):
        """
        Test that attempting to accept a request that doesn't exist returns a 404.
        """
        self.client.force_authenticate(user=self.user_receiver)
        nonexistent_url = reverse("friend-request-accept", kwargs={"request_pk": 9999})
        response = self.client.post(nonexistent_url)

        # get_object_or_404 in the view should handle this
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_accept_already_accepted_request(self):
        """
        Test that accepting a request that was already accepted results in a 404
        (because the request object is deleted).
        """
        # The receiver accepts the request successfully the first time
        self.client.force_authenticate(user=self.user_receiver)
        first_response = self.client.post(self.accept_url)
        self.assertEqual(first_response.status_code, status.HTTP_200_OK)

        # Now, try to accept it again
        second_response = self.client.post(self.accept_url)
        # The friend_request object no longer exists, so get_object_or_404 should trigger
        self.assertEqual(second_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_bulk_friend_acceptance_performance(self):
        """
        Test performance of accepting multiple friend requests with manual monitoring.
        
        Uses Mercury's manual monitoring for detailed performance insights.
        """
        # Create multiple friend requests for comprehensive performance testing
        bulk_senders = []
        bulk_requests = []
        
        for i in range(5):
            sender = User.objects.create_user(
                username=f"bulk_sender_{i}", password="password123"
            )
            bulk_senders.append(sender)
            sender_profile = UserProfile.objects.get(user=sender)
            
            request = ProfileFriendRequest.objects.create(
                sender=sender_profile, 
                receiver=self.profile_receiver
            )
            bulk_requests.append(request)
        
        self.client.force_authenticate(user=self.user_receiver)
        
        # Use manual monitoring for detailed performance analysis
        with monitor_django_view("bulk_friend_request_acceptance") as monitor:
            # Accept all friend requests sequentially
            for request in bulk_requests:
                accept_url = reverse(
                    "friend-request-accept", 
                    kwargs={"request_pk": request.pk}
                )
                response = self.client.post(accept_url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Access detailed metrics from manual monitoring
        metrics = monitor.metrics
        
        # Verify performance characteristics for bulk operations
        self.assertLess(metrics.response_time, 800, 
                       f"Bulk acceptance took {metrics.response_time}ms - too slow")
        self.assertLess(metrics.query_count, 60, 
                       f"Bulk acceptance used {metrics.query_count} queries - potential N+1")
        
        # Detailed performance analysis
        print(f"\\n📊 Bulk Friend Acceptance Performance:")
        print(f"   Response Time: {metrics.response_time:.2f}ms")
        print(f"   Query Count: {metrics.query_count}")
        print(f"   Memory Usage: {metrics.memory_usage:.2f}MB")
        print(f"   Performance Status: {metrics.performance_status.value}")
        
        # Assert memory efficiency for bulk operations
        self.assertMemoryEfficient(metrics)
        
        # Verify all friendships were established
        self.profile_receiver.refresh_from_db()
        receiver_friends = self.profile_receiver.friends.all()
        for sender in bulk_senders:
            self.assertIn(sender, receiver_friends,
                         f"Friendship with {sender.username} not established")

    def test_accept_with_per_test_thresholds(self):
        """
        Test with custom per-test performance thresholds for specific scenarios.
        """
        # Set stricter thresholds for this critical operation
        self.set_test_performance_thresholds({
            'response_time_ms': 100,     # Very strict for single acceptance
            'query_count_max': 8,        # Minimal queries expected
            'memory_overhead_mb': 20,    # Efficient memory usage
        })
        
        self.client.force_authenticate(user=self.user_receiver)
        
        # Mercury will automatically monitor with custom thresholds
        response = self.client.post(self.accept_url)
        
        # Standard verification
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Friend request accepted.")
