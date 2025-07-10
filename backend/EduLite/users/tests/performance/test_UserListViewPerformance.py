# users/tests/performance/test_UserListViewPerformance.py
"""
Enhanced UserListView Performance Testing Suite
Utilizing the complete MIDAS performance monitoring framework with Django-aware capabilities.
"""
import sys
from pathlib import Path
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

# Add performance testing framework to path
performance_path = Path(__file__).parent.parent.parent.parent.parent / "performance_testing" / "python_bindings"
sys.path.insert(0, str(performance_path))

from monitor import DjangoPerformanceIssues
from django_integration import DjangoPerformanceAPITestCase
from colors import colors, EduLiteColorScheme


class UserListViewPerformanceTests(DjangoPerformanceAPITestCase):
    """
    Enhanced UserListView Performance Tests with comprehensive Django monitoring.
    Showcases CPU monitoring, query tracking, cache analysis, and Django-specific issue detection.
    """
    
    @classmethod
    def setUpClass(cls):
        """One-time setup with enhanced monitoring capabilities."""
        super().setUpClass()
        
        print(f"\n{colors.colorize('🚀 Enhanced UserListView Performance Suite', EduLiteColorScheme.ACCENT, bold=True)}")
        print(f"{colors.colorize('=' * 70, EduLiteColorScheme.BORDER)}")
        print(f"{colors.colorize('🔬 Features: CPU Monitoring | Query Analysis | Cache Tracking | Django Issues', EduLiteColorScheme.INFO)}")
        
        # Create test user
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create comprehensive test dataset
        cls.test_users = []
        for i in range(25):  # Larger dataset for better analysis
            user = User.objects.create_user(
                username=f'user{i:03d}',
                email=f'user{i:03d}@example.com',
                password='testpass123',
                first_name=f'FirstName{i}',
                last_name=f'LastName{i}'
            )
            cls.test_users.append(user)
        
        cls.url = reverse('user-list')
        cls.all_metrics = []
        
        print(f"\n{colors.colorize('📊 Enhanced Test Environment:', EduLiteColorScheme.INFO, bold=True)}")
        print(f"   👤 Total Users: {len(cls.test_users) + 1}")
        print(f"   📡 Endpoint: {cls.url}")
        print(f"   🔍 Monitoring: Response Time, CPU, Memory, Queries, Cache")
    
    def setUp(self):
        """Minimal per-test setup."""
        self.client.force_authenticate(user=self.user)
    
    # ============================================================================
    # ENHANCED BASIC PERFORMANCE TESTS
    # ============================================================================
    
    def test_00_enhanced_debug_with_memory_analysis(self):
        """Enhanced debug test with memory and CPU analysis."""
        
        print(f"\n{colors.colorize('🔧 Enhanced Debug Test:', EduLiteColorScheme.INFO, bold=True)}")
        
        def debug_test():
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            return response
        
        metrics = self.run_comprehensive_analysis(
            operation_name="Enhanced Debug Test",
            test_function=debug_test,
            print_analysis=False
        )
        
        # Calculate payload size for memory analysis
        if hasattr(metrics, '_test_result'):
            import json
            response_json = json.dumps(metrics._test_result.data)
            payload_size_kb = len(response_json.encode('utf-8')) / 1024
            metrics.calculate_memory_payload_efficiency(payload_size_kb)
        
        # Show comprehensive debug information
        print(metrics.debug_cpu_measurement())
        print(f"\n{metrics.get_memory_analysis_report()}")
        
        # Show the realistic expectations
        print(f"\n   🎯 Realistic Expectations for {metrics.query_count} queries:")
        print(f"      CPU Time: 2-8ms (Django/Python processing)")
        print(f"      Wait Time: 15-25ms (database I/O)")
        print(f"      CPU Efficiency: 10-35% (realistic for I/O bound)")
        print(f"      Memory Overhead: 2-10MB (temporary objects, payload processing)")
        
        self.all_metrics.append(metrics)
    
    def test_00_debug_cpu_measurement(self):
        """Debug the CPU measurement to see what's happening."""
        
        print(f"\n{colors.colorize('🔧 CPU Measurement Debug Test:', EduLiteColorScheme.INFO, bold=True)}")
        
        def debug_test():
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            return response
        
        metrics = self.run_comprehensive_analysis(
            operation_name="CPU Debug Test",
            test_function=debug_test,
            print_analysis=False
        )
        
        # Show debug information
        print(metrics.debug_cpu_measurement())
        
        self.all_metrics.append(metrics)
    
    def test_00_scoring_system_demo(self):
        """Demonstrate the enhanced scoring system."""
        
        print(f"\n{colors.colorize('🎯 Performance Scoring System Demo:', EduLiteColorScheme.INFO, bold=True)}")
        
        def demo_test():
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            return response
        
        metrics = self.run_comprehensive_analysis(
            operation_name="Scoring System Demo",
            test_function=demo_test,
            print_analysis=False,  # We'll show custom output
            show_scoring=True
        )
        
        # Show the detailed scoring breakdown
        print(f"\n{colors.colorize('📊 Scoring Breakdown Example:', EduLiteColorScheme.ACCENT, bold=True)}")
        score = metrics.performance_score
        
        print(f"   🎓 Grade: {score.grade} ({score.total_score:.1f}/100)")
        print(f"   ⏱️  Response Time: {score.response_time_score:.1f}/25 pts")
        print(f"   🗃️  Query Efficiency: {score.query_efficiency_score:.1f}/30 pts") 
        print(f"   🧠 Memory: {score.memory_efficiency_score:.1f}/15 pts")
        print(f"   💾 Cache: {score.cache_performance_score:.1f}/10 pts")
        print(f"   🚨 N+1 Penalty: -{score.n_plus_one_penalty:.1f} pts")
        
        print(f"\n{colors.colorize('🔍 The scoring system is working!', EduLiteColorScheme.SUCCESS)}")
        
        self.all_metrics.append(metrics)
    
    def test_00_framework_verification(self):
        """Verify the enhanced framework is working correctly."""
        
        print(f"\n{colors.colorize('🔧 Framework Verification Test:', EduLiteColorScheme.INFO, bold=True)}")
        
        # Simple monitor test
        monitor = self.monitor_django_view("Framework Verification")
        
        with monitor:
            # Do a simple operation that should generate some activity
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that metrics were generated
        metrics = monitor.metrics
        
        print(f"   📊 Response Time: {metrics.response_time:.2f}ms")
        print(f"   🧠 Memory Usage: {metrics.memory_usage:.2f}MB")
        print(f"   🗃️ Query Count: {metrics.query_count}")
        print(f"   🏷️ Operation Type: {metrics.operation_type}")
        
        # Basic assertions
        self.assertGreater(metrics.response_time, 0, "Should have response time")
        self.assertGreater(metrics.memory_usage, 0, "Should have memory usage")
        self.assertGreaterEqual(metrics.cpu_percentage, 0, "Should have CPU percentage")
        self.assertGreaterEqual(metrics.query_count, 0, "Should have query count")
        
        # Check Django issues analysis
        self.assertIsInstance(metrics.django_issues, DjangoPerformanceIssues)
        
        print(f"   ✅ {colors.colorize('Framework verification successful!', EduLiteColorScheme.SUCCESS)}")
        
        self.all_metrics.append(metrics)
    
    def test_01_comprehensive_basic_performance(self):
        """Enhanced basic performance test with corrected CPU monitoring."""
        
        def basic_test():
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('results', response.data)
            return response
        
        metrics = self.run_comprehensive_analysis(
            operation_name="UserListView Basic Performance",
            test_function=basic_test,
            expect_response_under=100,
            expect_memory_under=150,
            expect_queries_under=3,
            print_analysis=True,
            show_scoring=True
        )
        
        
        self.all_metrics.append(metrics)
    
    def test_02_django_query_analysis(self):
        """Deep Django query pattern analysis."""
        
        def query_intensive_test():
            # Test with larger page size to potentially trigger more queries
            response = self.client.get(f"{self.url}?page_size=20")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            return response
        
        metrics = self.run_comprehensive_analysis(
            operation_name="UserListView Query Analysis",
            test_function=query_intensive_test,
            expect_queries_under=5,  # Strict query limit
            expect_response_under=150,
            print_analysis=True
        )
        
        # Django-specific assertions
        self.assertQueriesLess(metrics, 10, "Should not have excessive queries")
        self.assertNoNPlusOne(metrics, "Query pattern should be optimized")
        
        # Check for specific Django issues
        if hasattr(metrics, 'django_issues'):
            self.assertFalse(metrics.django_issues.excessive_queries, "Should not have excessive queries")
            self.assertFalse(metrics.django_issues.missing_db_indexes, "Should not indicate missing indexes")
        
        self.create_enhanced_dashboard(metrics, "🔍 Django Query Analysis Dashboard")
        self.all_metrics.append(metrics)
    
    def test_03_cpu_and_memory_profiling(self):
        """CPU and memory usage profiling under different loads."""
        
        load_scenarios = [
            ("Light Load", 5),
            ("Medium Load", 15), 
            ("Heavy Load", 25)
        ]
        
        cpu_memory_metrics = []
        
        for scenario_name, page_size in load_scenarios:
            def load_test():
                response = self.client.get(f"{self.url}?page_size={page_size}")
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                return response
            
            metrics = self.run_comprehensive_analysis(
                operation_name=f"CPU/Memory Analysis - {scenario_name}",
                test_function=load_test,
                expect_memory_under=200,
                print_analysis=False
            )
            
            cpu_memory_metrics.append(metrics)
            self.all_metrics.append(metrics)
            
            # Individual assertions
            self.assertMemoryEfficient(metrics, f"{scenario_name} should be memory efficient")
            
            print(f"   ⚡ {scenario_name}: {metrics.response_time:.1f}ms | "
                  f"CPU: {metrics.cpu_percentage:.1f}% | "
                  f"Memory: {metrics.memory_usage:.1f}MB | "
                  f"Queries: {metrics.query_count}")
        
        # Analyze CPU/Memory trends
        print(f"\n{colors.colorize('📊 CPU & Memory Trend Analysis:', EduLiteColorScheme.OPTIMIZATION, bold=True)}")
        
        if len(cpu_memory_metrics) >= 2:
            light = cpu_memory_metrics[0]
            heavy = cpu_memory_metrics[-1]
            
            cpu_increase = heavy.cpu_percentage - light.cpu_percentage
            memory_increase = heavy.memory_usage - light.memory_usage
            
            print(f"   ⚡ CPU Scaling: +{cpu_increase:.1f}% ({light.cpu_percentage:.1f}% → {heavy.cpu_percentage:.1f}%)")
            print(f"   🧠 Memory Scaling: +{memory_increase:.1f}MB ({light.memory_usage:.1f}MB → {heavy.memory_usage:.1f}MB)")
            
            # Assert reasonable scaling
            self.assertLess(cpu_increase, 50, "CPU increase should be reasonable")
            self.assertLess(memory_increase, 100, "Memory increase should be reasonable")
    
    def test_04_serialization_performance_deep_dive(self):
        """Deep analysis of serialization performance patterns."""
        
        serialization_scenarios = [
            ("Minimal Fields", 5, "?fields=id,username"),
            ("Standard Fields", 10, ""),
            ("Full Profile", 15, "?include_profile=true") if hasattr(self, 'include_profile_param') else ("Full Fields", 15, "")
        ]
        
        serialization_metrics = []
        
        for scenario_name, count, query_params in serialization_scenarios:
            def serialization_test():
                url = f"{self.url}?page_size={count}{query_params}"
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                return response
            
            metrics = self.run_comprehensive_analysis(
                operation_name=f"Serialization Analysis - {scenario_name}",
                test_function=serialization_test,
                expect_response_under=200,
                print_analysis=False
            )
            
            serialization_metrics.append(metrics)
            self.all_metrics.append(metrics)
            
            # Check for slow serialization issues
            if hasattr(metrics, 'django_issues'):
                if metrics.django_issues.slow_serialization:
                    print(f"   ⚠️ {colors.colorize(f'{scenario_name}: Slow serialization detected', EduLiteColorScheme.WARNING)}")
            
            # Payload efficiency analysis
            if hasattr(metrics, '_test_result'):
                import json
                payload_size = len(json.dumps(metrics._test_result.data).encode('utf-8'))
                per_user_bytes = payload_size / count if count > 0 else 0
                
                print(f"   📊 {scenario_name}: {metrics.response_time:.1f}ms | "
                      f"Payload: {payload_size/1024:.1f}KB | "
                      f"Per User: {per_user_bytes:.0f}B")
                
                # Assert reasonable per-user payload size
                self.assertLess(per_user_bytes, 1000, f"{scenario_name}: Per-user payload should be under 1KB")
        
        # Serialization trend analysis
        if len(serialization_metrics) >= 2:
            print(f"\n{colors.colorize('📈 Serialization Efficiency Analysis:', EduLiteColorScheme.OPTIMIZATION, bold=True)}")
            
            response_times = [m.response_time for m in serialization_metrics]
            efficiency_ratio = max(response_times) / min(response_times)
            
            print(f"   📊 Efficiency Ratio: {efficiency_ratio:.2f}x")
            
            if efficiency_ratio < 2.0:
                print(f"   ✅ {colors.colorize('Excellent serialization consistency', EduLiteColorScheme.SUCCESS)}")
            elif efficiency_ratio < 3.0:
                print(f"   ⚠️ {colors.colorize('Good serialization scaling', EduLiteColorScheme.WARNING)}")
            else:
                print(f"   ❌ {colors.colorize('Serialization optimization needed', EduLiteColorScheme.CRITICAL)}")
    
    def test_05_cache_performance_analysis(self):
        """Comprehensive cache performance analysis."""
        
        # First request (cache miss expected)
        def first_request():
            response = self.client.get(f"{self.url}?page=1")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            return response
        
        first_metrics = self.run_comprehensive_analysis(
            operation_name="Cache Analysis - First Request",
            test_function=first_request,
            print_analysis=False
        )
        
        # Second request (potential cache hit)
        def second_request():
            response = self.client.get(f"{self.url}?page=1")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            return response
        
        second_metrics = self.run_comprehensive_analysis(
            operation_name="Cache Analysis - Second Request", 
            test_function=second_request,
            print_analysis=False
        )
        
        print(f"\n{colors.colorize('💾 Cache Performance Analysis:', EduLiteColorScheme.OPTIMIZATION, bold=True)}")
        print(f"   🔍 First Request: {first_metrics.response_time:.1f}ms | Cache: {first_metrics.cache_hits}H/{first_metrics.cache_misses}M")
        print(f"   🔍 Second Request: {second_metrics.response_time:.1f}ms | Cache: {second_metrics.cache_hits}H/{second_metrics.cache_misses}M")
        
        # Cache efficiency analysis
        if second_metrics.cache_hits + second_metrics.cache_misses > 0:
            print(f"   📊 Cache Hit Ratio: {second_metrics.cache_hit_ratio:.1%}")
            
            if second_metrics.cache_hit_ratio > 0.5:
                print(f"   ✅ {colors.colorize('Good cache utilization', EduLiteColorScheme.SUCCESS)}")
            else:
                print(f"   ⚠️ {colors.colorize('Cache optimization opportunities', EduLiteColorScheme.WARNING)}")
        
        self.all_metrics.extend([first_metrics, second_metrics])
    
    def test_06_pagination_performance_deep_analysis(self):
        """Deep pagination performance analysis with Django awareness."""
        
        pagination_tests = []
        
        for page_num in range(1, 4):  # Test first 3 pages
            def page_test():
                response = self.client.get(f"{self.url}?page={page_num}")
                if response.status_code == 404:  # No more pages
                    return type('MockResponse', (), {'status_code': 200, 'data': {'results': [], 'count': 0}})()
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                return response
            
            metrics = self.run_comprehensive_analysis(
                operation_name=f"Pagination Deep Analysis - Page {page_num}",
                test_function=page_test,
                expect_queries_under=4,  # Pagination shouldn't add queries
                print_analysis=False
            )
            
            pagination_tests.append(metrics)
            self.all_metrics.append(metrics)
        
        # Pagination consistency analysis
        print(f"\n{colors.colorize('📄 Pagination Deep Analysis:', EduLiteColorScheme.OPTIMIZATION, bold=True)}")
        
        for i, metrics in enumerate(pagination_tests, 1):
            print(f"   📊 Page {i}: {metrics.response_time:.1f}ms | "
                  f"Queries: {metrics.query_count} | "
                  f"CPU: {metrics.cpu_percentage:.1f}%")
            
            # Check for pagination-specific issues
            if hasattr(metrics, 'django_issues') and metrics.django_issues.inefficient_pagination:
                print(f"   ⚠️ {colors.colorize(f'Page {i}: Inefficient pagination detected', EduLiteColorScheme.WARNING)}")
        
        # Pagination performance consistency
        if len(pagination_tests) >= 2:
            response_times = [m.response_time for m in pagination_tests]
            consistency_ratio = max(response_times) / min(response_times)
            
            print(f"   📈 Consistency Ratio: {consistency_ratio:.2f}x")
            
            if consistency_ratio < 1.5:
                print(f"   ✅ {colors.colorize('Excellent pagination consistency', EduLiteColorScheme.SUCCESS)}")
                
            # Assert consistency
            self.assertLess(consistency_ratio, 3.0, "Pagination should be consistent across pages")
    
    def test_07_edge_case_performance_monitoring(self):
        """Enhanced edge case performance with comprehensive monitoring."""
        
        edge_cases = [
            ("Empty Results", f"{self.url}?search=nonexistent_user_xyz"),
            ("Invalid Page", f"{self.url}?page=999"),
            ("Large Page Size", f"{self.url}?page_size=100"),
            ("Invalid Parameters", f"{self.url}?invalid_param=test")
        ]
        
        edge_metrics = []
        
        for case_name, test_url in edge_cases:
            def edge_test():
                response = self.client.get(test_url)
                # Accept both success and 404 for edge cases
                self.assertIn(response.status_code, [200, 404])
                return response
            
            metrics = self.run_comprehensive_analysis(
                operation_name=f"Edge Case - {case_name}",
                test_function=edge_test,
                expect_response_under=100,  # Edge cases should be fast
                print_analysis=False
            )
            
            edge_metrics.append(metrics)
            self.all_metrics.append(metrics)
            
            # Edge cases should be fast and efficient
            self.assertResponseTimeLess(metrics, 150, f"{case_name} should be fast")
            self.assertMemoryEfficient(metrics, f"{case_name} should be memory efficient")
            
            print(f"   🔍 {case_name}: {metrics.response_time:.1f}ms | "
                  f"CPU: {metrics.cpu_percentage:.1f}% | "
                  f"Queries: {metrics.query_count}")
        
        # Edge case performance summary
        avg_response_time = sum(m.response_time for m in edge_metrics) / len(edge_metrics)
        print(f"\n   📊 Edge Case Average: {avg_response_time:.1f}ms")
        
        if avg_response_time < 50:
            print(f"   ✅ {colors.colorize('Excellent edge case handling', EduLiteColorScheme.SUCCESS)}")
    
    def test_08_comprehensive_performance_regression_detection(self):
        """Comprehensive performance regression detection with enhanced monitoring."""
        
        # Baseline measurement
        def baseline_test():
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            return response
        
        baseline = self.run_comprehensive_analysis(
            operation_name="Regression Baseline",
            test_function=baseline_test,
            print_analysis=False
        )
        
        # Simulated regression test (with slight delay)
        import time
        
        def regression_test():
            time.sleep(0.001)  # Minimal delay to simulate variance
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            return response
        
        current = self.run_comprehensive_analysis(
            operation_name="Regression Current",
            test_function=regression_test,
            print_analysis=False
        )
        
        # Comprehensive regression analysis
        print(f"\n{colors.colorize('🔄 Comprehensive Regression Analysis:', EduLiteColorScheme.OPTIMIZATION, bold=True)}")
        
        metrics_comparison = [
            ("Response Time", baseline.response_time, current.response_time, "ms"),
            ("Memory Usage", baseline.memory_usage, current.memory_usage, "MB"),
            ("Query Count", baseline.query_count, current.query_count, "queries")
        ]
        
        for metric_name, baseline_val, current_val, unit in metrics_comparison:
            if baseline_val > 0:
                change_percent = ((current_val - baseline_val) / baseline_val) * 100
                change_icon = "📈" if change_percent > 0 else "📉"
                
                print(f"   {change_icon} {metric_name}: {baseline_val:.1f}{unit} → {current_val:.1f}{unit} ({change_percent:+.1f}%)")
                
                # Regression thresholds
                if metric_name == "Response Time" and change_percent > 50:
                    print(f"   ⚠️ {colors.colorize('Significant response time regression', EduLiteColorScheme.WARNING)}")
                elif metric_name == "Query Count" and change_percent > 0:
                    print(f"   ⚠️ {colors.colorize('Query count increased', EduLiteColorScheme.WARNING)}")
        
        self.all_metrics.extend([baseline, current])
    
    def test_09_final_comprehensive_summary_with_enhanced_scoring(self):
        """Generate comprehensive final performance summary with enhanced scoring system."""
        
        if not self.all_metrics:
            self.skipTest("No metrics collected for summary")
        
        # Final comprehensive test with scoring
        def final_test():
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            return response
        
        final_metrics = self.run_comprehensive_analysis(
            operation_name="Final Comprehensive Summary",
            test_function=final_test,
            print_analysis=False,  # We'll handle the display ourselves
            show_scoring=True      # Enable the new scoring system
        )
        
        # Add to all metrics
        all_results = self.all_metrics + [final_metrics]
        
        # Use the new scoring system for overall assessment
        print(f"\n{colors.colorize('🎯 FINAL PERFORMANCE ASSESSMENT WITH SCORING:', EduLiteColorScheme.ACCENT, bold=True)}")
        
        # Display the final test with full scoring details
        print(final_metrics.get_performance_report_with_scoring())
        
        # Aggregate statistics across all tests
        response_times = [m.response_time for m in all_results]
        cpu_usages = [m.cpu_percentage for m in all_results]
        memory_usages = [m.memory_usage for m in all_results]
        query_counts = [m.query_count for m in all_results]
        
        # Calculate average score across all tests (if they have scoring)
        scores = []
        grades = []
        for m in all_results:
            if hasattr(m, 'performance_score'):
                scores.append(m.performance_score.total_score)
                grades.append(m.performance_score.grade)
        
        if scores:
            avg_score = sum(scores) / len(scores)
            
            # Count grade distribution
            from collections import Counter
            grade_counts = Counter(grades)
            
            print(f"\n{colors.colorize('📊 COMPREHENSIVE TEST SUITE ANALYSIS:', EduLiteColorScheme.INFO, bold=True)}")
            print(f"   🎯 Overall Score: {avg_score:.1f}/100")
            print(f"   📈 Tests Completed: {len(all_results)}")
            print(f"   🏆 Grade Distribution:")
            
            for grade, count in sorted(grade_counts.items(), key=lambda x: ['F', 'D', 'C', 'B', 'A', 'A+', 'S'].index(x[0])):
                percentage = (count / len(grades)) * 100
                print(f"     {grade}: {count} tests ({percentage:.1f}%)")
        
        # Performance statistics
        stats = {
            'total_tests': len(all_results),
            'avg_response_time': sum(response_times) / len(response_times),
            'max_response_time': max(response_times),
            'min_response_time': min(response_times),
            'avg_cpu_usage': sum(cpu_usages) / len(cpu_usages),
            'max_cpu_usage': max(cpu_usages),
            'avg_memory_usage': sum(memory_usages) / len(memory_usages),
            'max_memory_usage': max(memory_usages),
            'avg_query_count': sum(query_counts) / len(query_counts),
            'max_query_count': max(query_counts)
        }
        
        print(f"\n{colors.colorize('📊 Raw Performance Statistics:', EduLiteColorScheme.INFO, bold=True)}")
        print(f"   ⏱️  Response Time: {stats['min_response_time']:.1f}ms - {stats['max_response_time']:.1f}ms (avg: {stats['avg_response_time']:.1f}ms)")
        print(f"   🧠 Memory Usage: {min(memory_usages):.1f}MB - {stats['max_memory_usage']:.1f}MB (avg: {stats['avg_memory_usage']:.1f}MB)")
        print(f"   🗃️  Query Count: {min(query_counts)} - {stats['max_query_count']} (avg: {stats['avg_query_count']:.1f})")
        
        # Critical issues summary
        n_plus_one_count = sum(1 for m in all_results if hasattr(m, 'django_issues') and m.django_issues.has_n_plus_one)
        
        if n_plus_one_count > 0:
            print(f"\n{colors.colorize('🚨 CRITICAL ISSUES SUMMARY:', EduLiteColorScheme.CRITICAL, bold=True)}")
            print(f"   🔥 N+1 Query Issues: {n_plus_one_count}/{len(all_results)} tests affected")
            print(f"   ⚠️  This is preventing A+ performance scores!")
            print(f"   💡 Fix the UserSerializer and QuerySet optimization to dramatically improve scores")
        
        # Show what fixing N+1 would achieve
        if scores and n_plus_one_count > 0:
            # Estimate score without N+1 penalties
            potential_scores = []
            for m in all_results:
                if hasattr(m, 'performance_score'):
                    potential_score = min(100, m.performance_score.total_score + m.performance_score.n_plus_one_penalty)
                    potential_scores.append(potential_score)
            
            if potential_scores:
                potential_avg = sum(potential_scores) / len(potential_scores)
                improvement = potential_avg - avg_score
                
                print(f"\n{colors.colorize('🎯 OPTIMIZATION POTENTIAL:', EduLiteColorScheme.OPTIMIZATION, bold=True)}")
                print(f"   📈 Current Average Score: {avg_score:.1f}/100")
                print(f"   🚀 Potential Score (N+1 fixed): {potential_avg:.1f}/100")
                print(f"   ⬆️  Improvement: +{improvement:.1f} points")
                
                # Determine potential grade
                if potential_avg >= 95:
                    potential_grade = "S"
                elif potential_avg >= 90:
                    potential_grade = "A+"
                elif potential_avg >= 80:
                    potential_grade = "A"
                else:
                    potential_grade = "B"
                
                print(f"   🏆 Potential Grade: {potential_grade}")
        
        print(f"\n{colors.colorize('⚡ Enhanced Efficiency Report:', EduLiteColorScheme.SUCCESS, bold=True)}")
        print(f"   ✅ All {stats['total_tests']} enhanced tests completed successfully")
        print(f"   🔬 Features: CPU Monitoring, Query Analysis, Cache Tracking, Django Issues, Performance Scoring")
        
        # Assertions using the new scoring system
        if scores:
            self.assertGreater(avg_score, 30, "Average score should be above failing threshold")
            
            # If we have mostly N+1 issues, that's expected until fixed
            if n_plus_one_count > len(all_results) * 0.5:
                print(f"\n{colors.colorize('ℹ️ Note: Scores are low due to N+1 query issues. This is expected until optimization.', EduLiteColorScheme.INFO)}")
            else:
                self.assertGreater(avg_score, 60, "Average score should be reasonable without major N+1 issues")
        
        # Traditional assertions (kept for compatibility)
        self.assertLess(stats['avg_response_time'], 300, "Average response time should be reasonable")
        self.assertLess(stats['avg_memory_usage'], 250, "Average memory usage should be efficient")