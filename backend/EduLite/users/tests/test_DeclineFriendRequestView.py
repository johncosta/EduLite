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

User = get_user_model()


class DeclineFriendRequestViewMercuryTests(DjangoMercuryAPITestCase):
    """
    Mercury Performance Test Suite for DeclineFriendRequestView
    
    Specialized monitoring for DELETE operations with focus on:
    - Database cleanup operation performance
    - CASCADE deletion efficiency (Mercury gives delete operations special consideration)
    - Object deletion and cleanup query patterns
    - Memory efficiency during deletion operations
    - Notification cleanup performance (if applicable)
    """

    @classmethod
    def setUpClass(cls):
        """Configure Mercury specifically for delete operation monitoring."""
        super().setUpClass()
        
        # Configure Mercury with special considerations for DELETE operations
        cls.configure_mercury(
            enabled=True,
            auto_scoring=True,
            auto_threshold_adjustment=True,   # Mercury automatically adjusts for delete operations
            store_history=True,               # Track deletion operation trends
            generate_summaries=True,          # Executive insights on deletion performance
            verbose_reporting=False,          
            educational_guidance=True         # Learn delete operation optimization patterns
        )
        
        # Set performance thresholds optimized for deletion operations
        # Note: Mercury automatically provides more lenient thresholds for delete_view operations
        cls.set_performance_thresholds({
            'response_time_ms': 150,          # Delete operations should still be reasonably fast
            'query_count_max': 12,            # Allow for cleanup queries but avoid N+1
            'memory_overhead_mb': 25,         # Minimal memory overhead for deletions
        })

    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole test class."""
        # Create users and get their profiles (created via signal)
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
        cls.profile_unrelated = UserProfile.objects.get(user=cls.user_unrelated)

        # Create a persistent friend request for most tests
        cls.friend_request = ProfileFriendRequest.objects.create(
            sender=cls.profile_sender, receiver=cls.profile_receiver
        )
        cls.decline_url = reverse(
            "friend-request-decline", kwargs={"request_pk": cls.friend_request.pk}
        )

    def test_decline_request_unauthenticated(self):
        """
        Test that an unauthenticated user cannot decline a friend request.
        """
        response = self.client.post(self.decline_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_receiver_decline_performance_analysis(self):
        """
        Test friend request decline with specialized delete operation monitoring.
        
        Mercury's delete operation analysis focuses on:
        - Database cleanup efficiency
        - CASCADE operation performance (Mercury gives delete operations special consideration)
        - Memory efficiency during object deletion
        - Query pattern optimization for deletion
        """
        self.client.force_authenticate(user=self.user_receiver)
        
        # Use comprehensive analysis with delete_view operation type
        metrics = self.run_comprehensive_analysis(
            operation_name="FriendRequestDecline",
            test_function=lambda: self.client.post(self.decline_url),
            operation_type="delete_view",         # Mercury provides special handling for deletes
            expect_response_under=120,            # Delete should be fast
            expect_queries_under=8,               # Minimal cleanup queries
            expect_memory_under=80,               # Efficient deletion
            print_analysis=False,
            show_scoring=True,
            auto_detect_n_plus_one=True           # Check for deletion N+1 patterns
        )

        # Standard functionality verification
        response = metrics._test_result
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Friend request declined successfully.")

        # Verify the deletion was successful
        with self.assertRaises(ProfileFriendRequest.DoesNotExist):
            ProfileFriendRequest.objects.get(pk=self.friend_request.pk)

        # Assert production-ready performance for deletion operations
        self.assert_mercury_performance_production_ready(metrics)
        
        # Ensure efficient deletion (no unnecessary queries)
        self.assertPerformanceFast(metrics)
        self.assertMemoryEfficient(metrics)

    def test_sender_can_cancel_request(self):
        """
        Test that the original sender of a request can successfully cancel it.
        """
        self.client.force_authenticate(user=self.user_sender)
        response = self.client.post(self.decline_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["detail"], "Friend request canceled successfully."
        )

        # Verify the request object has been deleted
        self.assertFalse(
            ProfileFriendRequest.objects.filter(pk=self.friend_request.pk).exists()
        )

    def test_unrelated_user_cannot_decline_request(self):
        """
        Test that a user who is neither the sender nor the receiver cannot decline the request.
        """
        self.client.force_authenticate(user=self.user_unrelated)
        response = self.client.post(self.decline_url)
        # This tests the IsFriendRequestReceiverOrSender permission
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_decline_nonexistent_request(self):
        """
        Test that attempting to decline a request that doesn't exist returns a 404.
        """
        self.client.force_authenticate(user=self.user_sender)
        nonexistent_url = reverse("friend-request-decline", kwargs={"request_pk": 9999})
        response = self.client.post(nonexistent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_decline_already_actioned_request(self):
        """
        Test that declining a request that was already declined/accepted results in a 404.
        """
        # First, the receiver declines the request successfully
        self.client.force_authenticate(user=self.user_receiver)
        self.client.post(self.decline_url)

        # Now, the sender tries to cancel the same, now-deleted request
        self.client.force_authenticate(user=self.user_sender)
        response = self.client.post(self.decline_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_decline_with_get_method_not_allowed(self):
        """
        Test that using GET on the decline endpoint is not allowed.
        """
        self.client.force_authenticate(user=self.user_receiver)
        response = self.client.get(self.decline_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_bulk_decline_operations_performance(self):
        """
        Test performance of multiple decline operations with manual monitoring.
        
        Analyzes deletion operation efficiency when processing multiple requests.
        """
        # Create multiple friend requests for bulk deletion testing
        bulk_senders = []
        bulk_requests = []
        
        for i in range(4):
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
        
        # Use manual monitoring for detailed deletion performance analysis
        with monitor_django_view("bulk_friend_request_decline") as monitor:
            # Decline all friend requests sequentially
            declined_responses = []
            for request in bulk_requests:
                decline_url = reverse(
                    "friend-request-decline", 
                    kwargs={"request_pk": request.pk}
                )
                response = self.client.post(decline_url)
                declined_responses.append(response)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Access detailed metrics from manual monitoring
        metrics = monitor.metrics
        
        # Analyze bulk deletion performance characteristics
        print(f"\\n🗑️  Bulk Friend Request Decline Performance:")
        print(f"   ⏱️  Total Time: {metrics.response_time:.2f}ms")
        print(f"   🗃️  Database Queries: {metrics.query_count}")
        print(f"   🧠 Memory Usage: {metrics.memory_usage:.2f}MB")
        print(f"   📊 Queries per Deletion: {metrics.query_count / len(bulk_requests):.1f}")
        print(f"   ⚡ Performance Status: {metrics.performance_status.value}")
        
        # Performance assertions for bulk deletion operations
        self.assertLess(metrics.response_time, 600, 
                       f"Bulk decline took {metrics.response_time}ms - too slow for {len(bulk_requests)} deletions")
        self.assertLess(metrics.query_count, 25, 
                       f"Used {metrics.query_count} queries for {len(bulk_requests)} deletions - potential N+1")
        
        # Verify all requests were deleted successfully
        for request in bulk_requests:
            self.assertFalse(
                ProfileFriendRequest.objects.filter(pk=request.pk).exists(),
                f"Request {request.pk} was not properly deleted"
            )
        
        # Assert memory efficiency for bulk deletion
        self.assertMemoryEfficient(metrics)

    def test_delete_operation_with_strict_thresholds(self):
        """
        Test deletion with custom per-test thresholds for critical scenarios.
        """
        # Create a fresh request for this test
        fresh_sender = User.objects.create_user(
            username="fresh_sender", password="password123"
        )
        fresh_sender_profile = UserProfile.objects.get(user=fresh_sender)
        fresh_request = ProfileFriendRequest.objects.create(
            sender=fresh_sender_profile, receiver=self.profile_receiver
        )
        
        # Set very strict thresholds for critical deletion operations
        self.set_test_performance_thresholds({
            'response_time_ms': 80,      # Very strict for single deletion
            'query_count_max': 5,        # Minimal deletion queries
            'memory_overhead_mb': 15,    # Efficient memory usage
        })
        
        self.client.force_authenticate(user=self.user_receiver)
        
        fresh_decline_url = reverse(
            "friend-request-decline", 
            kwargs={"request_pk": fresh_request.pk}
        )
        
        # Mercury will automatically monitor with custom thresholds
        response = self.client.post(fresh_decline_url)
        
        # Standard verification
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Friend request declined successfully.")
        
        # Verify deletion
        self.assertFalse(
            ProfileFriendRequest.objects.filter(pk=fresh_request.pk).exists()
        )

    def test_decline_with_put_method_not_allowed(self):
        """
        Test that using PUT on the decline endpoint is not allowed.
        """
        self.client.force_authenticate(user=self.user_receiver)
        response = self.client.put(self.decline_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
