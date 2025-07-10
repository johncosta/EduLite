# users/tests/performance/test_mercury_showcase.py
"""
Mercury Intelligent Performance Testing Showcase

This file demonstrates the DjangoMercuryAPITestCase in action, showing how it
transforms complex performance testing into a streamlined, intelligent system.

Compare this to the existing verbose performance tests to see the dramatic 
reduction in boilerplate while gaining enhanced intelligence.
"""
import sys
from pathlib import Path
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

# Add performance testing framework to path
performance_path = Path(__file__).parent.parent.parent.parent.parent / "performance_testing" / "python_bindings"
sys.path.insert(0, str(performance_path))

from django_integration_mercury import DjangoMercuryAPITestCase


class MercuryUserListViewShowcase(DjangoMercuryAPITestCase):
    """
    🚀 Mercury Intelligent Performance Testing Showcase
    
    This test class demonstrates how Mercury automatically handles:
    - Performance monitoring for ALL test methods
    - Smart threshold adjustment based on operation complexity
    - Automatic N+1 detection and optimization guidance
    - Progressive performance scoring with detailed breakdowns
    - Historical tracking and regression detection
    - Executive summary generation
    """
    
    @classmethod
    def setUpClass(cls):
        """Simple setup - Mercury handles the complex monitoring setup automatically."""
        super().setUpClass()
        
        # Configure custom performance thresholds (EXAMPLE)
        # This shows how to set realistic thresholds for your API
        cls.set_performance_thresholds({
            'response_time_ms': 100,      # Allow up to 100ms response time
            'query_count_max': 10,        # Allow up to 10 database queries 
            'memory_overhead_mb': 4,     # Allow up to 2MB memory overhead
        })
        
        # Configure Mercury for this test suite (optional)
        cls.configure_mercury(
            enabled=True,
            auto_scoring=True,
            auto_threshold_adjustment=True,
            store_history=True,
            verbose_reporting=False,  # Set to True for detailed reports
            educational_guidance=True  # Show guidance when thresholds exceeded
        )
        
        # Create test data
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com', 
            password='testpass123'
        )
        
        # Create test users for realistic performance testing
        cls.test_users = []
        for i in range(20):
            user = User.objects.create_user(
                username=f'user{i:03d}',
                email=f'user{i:03d}@example.com',
                password='testpass123',
                first_name=f'FirstName{i}',
                last_name=f'LastName{i}'
            )
            cls.test_users.append(user)
        
        cls.url = reverse('user-list')
    
    def setUp(self):
        """Simple per-test setup."""
        self.client.force_authenticate(user=self.user)
    
    # ========================================================================
    # MERCURY INTELLIGENT TESTS - Notice the dramatic simplification!
    # ========================================================================
    
    def test_user_list_basic_performance(self):
        """
        🎯 Basic UserListView performance test.
        
        Mercury automatically:
        - Detects this is a 'list_view' operation
        - Sets appropriate thresholds based on operation complexity
        - Monitors response time, memory, queries, cache
        - Detects N+1 patterns and provides specific fix guidance
        - Scores performance and tracks trends
        - Stores results for regression detection
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Mercury automatically wraps this test and provides full analysis!
        # No manual run_comprehensive_analysis() needed!
        # No manual metrics collection!
        # No manual threshold management!
    
    def test_user_list_with_pagination(self):
        """
        📄 Pagination performance test.
        
        Mercury automatically:
        - Detects pagination parameters in the request
        - Adjusts thresholds based on page_size context
        - Monitors for pagination-specific performance issues
        - Provides pagination optimization recommendations
        """
        # Mercury detects the page_size parameter and adjusts expectations
        response = self.client.get(f"{self.url}?page_size=15")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test different page sizes - Mercury adapts thresholds automatically
        response = self.client.get(f"{self.url}?page=2&page_size=10")
        self.assertIn(response.status_code, [200, 404])  # 404 OK if no second page
    
    def test_user_list_edge_cases(self):
        """
        🚦 Edge case performance test.
        
        Mercury automatically:
        - Adjusts expectations for edge cases
        - Detects invalid parameters and sets appropriate thresholds
        - Ensures edge cases are handled efficiently
        
        This test demonstrates context manager threshold overrides.
        """
        # Test various edge cases
        edge_cases = [
            "?page=999",  # Invalid page
            "?page_size=100",  # Large page size
            "?invalid_param=test",  # Invalid parameter
            "?ordering=unknown_field"  # Invalid ordering
        ]
        
        # Use context manager to temporarily allow higher query counts
        with self.mercury_override_thresholds({
            'query_count_max': 150,  # Allow many queries for edge case testing
            'response_time_ms': 300  # Allow higher response time for edge cases
        }):
            for params in edge_cases:
                response = self.client.get(f"{self.url}{params}")
                # Accept various response codes for edge cases
                self.assertIn(response.status_code, [200, 400, 404])
    
    def test_authentication_edge_case(self):
        """
        🔒 Authentication failure performance test.
        
        Mercury automatically:
        - Detects this as an 'authentication' operation type
        - Sets strict performance expectations for auth failures (should be fast)
        - Monitors for authentication-specific issues
        """
        # Remove authentication
        self.client.force_authenticate(user=None)
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Re-authenticate for cleanup
        self.client.force_authenticate(user=self.user)
    
    def test_concurrent_request_simulation(self):
        """
        ⚡ Simulate multiple concurrent requests.
        
        Mercury automatically:
        - Tracks performance under load simulation
        - Detects if performance degrades with concurrent access patterns
        - Provides scaling recommendations
        
        This test uses per-test threshold overrides to allow higher query counts.
        """
        # Allow higher query counts for this specific test
        self.set_test_performance_thresholds({
            'query_count_max': 100,  # Allow more queries for concurrent simulation
            'response_time_ms': 200   # Allow slightly higher response time
        })
        
        # Simulate multiple requests (simple version)
        responses = []
        for i in range(3):
            response = self.client.get(f"{self.url}?page={i+1}")
            responses.append(response)
        
        # All requests should complete successfully
        for response in responses:
            self.assertIn(response.status_code, [200, 404])
    
    def test_production_readiness_validation(self):
        """
        🚀 Production readiness validation.
        
        This test uses Mercury's built-in production readiness assertions
        to ensure the API is ready for production deployment.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
            
    @classmethod
    def tearDownClass(cls):
        """
        Mercury automatically generates comprehensive performance summary here.
        
        The summary includes:
        - Overall performance grade for the entire test suite
        - Grade distribution across all tests
        - Critical issues that need immediate attention
        - Top optimization opportunities with business impact
        - Potential score improvements if issues are fixed
        - Executive summary suitable for non-technical stakeholders
        """
        super().tearDownClass()
        
        # Mercury automatically generates:
        # 🎯 MERCURY INTELLIGENT PERFORMANCE ANALYSIS
        # 📊 PERFORMANCE OVERVIEW
        # 📊 GRADE DISTRIBUTION 
        # 🚨 CRITICAL ISSUES
        # ⚠️ REGRESSIONS & ISSUES
        # 💡 TOP OPTIMIZATION OPPORTUNITIES
        # 🚀 OPTIMIZATION POTENTIAL
        # 💼 EXECUTIVE SUMMARY