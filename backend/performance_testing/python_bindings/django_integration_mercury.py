# backend/performance_testing/python_bindings/django_integration_mercury.py
# A streamlined, intelligent system that automatically handles performance monitoring, scoring, analysis, and optimization guidance with minimal boilerplate code.

import time
import sys
import json
import sqlite3
import inspect

from pathlib import Path
from typing import Optional, Dict, Any, List, Callable, Union, Tuple
from dataclasses import dataclass, asdict
from functools import wraps

from django.test import TestCase

from rest_framework.test import APITestCase
from rest_framework.response import Response

from django_integration import DjangoPerformanceAPITestCase
from monitor import EnhancedPerformanceMetrics_Python, EnhancedPerformanceMonitor
from monitor import monitor_django_view, DjangoPerformanceIssues, PerformanceScore
from colors import colors, EduLiteColorScheme

try: # to import django settings
    from django.conf import settings

    if getattr(settings, 'MERCURY_HISTORY_PATH', None):
        mercury_history_path = Path(settings.MERCURY_HISTORY_PATH)
    else:
        print("No MERCURY_HISTORY_PATH found in Django settings. Using default path.")
        mercury_history_path = Path(__file__).parent.parent.parent / "logs" / "mercury_performance.db"
except ImportError:
    print("Django settings not found. Please make sure you have installed Django.")


@dataclass
class PerformanceBaseline:
    """Historical performance baseline for specific operation types."""
    operation_type: str
    avg_response_time: float
    avg_memory_usage: float
    avg_query_count: float
    sample_count: int
    last_updated: str
    
    def update_with_new_measurement(self, metrics: EnhancedPerformanceMetrics_Python):
        """Update baseline with new measurement using weighted average."""
        weight = 0.1  # Give 10% weight to new measurement
        self.avg_response_time = (1 - weight) * self.avg_response_time + weight * metrics.response_time
        self.avg_memory_usage = (1 - weight) * self.avg_memory_usage + weight * metrics.memory_usage
        self.avg_query_count = (1 - weight) * self.avg_query_count + weight * metrics.query_count
        self.sample_count += 1
        
        from datetime import datetime
        self.last_updated = datetime.now().isoformat()


@dataclass 
class OperationProfile:
    """Smart operation profile that adapts thresholds based on complexity."""
    operation_name: str
    expected_query_range: Tuple[int, int]  # (min, max) expected queries
    response_time_baseline: float  # Expected baseline response time
    memory_overhead_tolerance: float  # Acceptable memory overhead
    complexity_factors: Dict[str, Any]  # Factors affecting complexity
    
    def calculate_dynamic_thresholds(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Calculate dynamic thresholds based on operation context."""
        # Base thresholds
        thresholds = {
            'response_time': self.response_time_baseline,
            'memory_usage': 80 + self.memory_overhead_tolerance,  # Django baseline + tolerance
            'query_count': self.expected_query_range[1],
        }
        
        # Adjust based on context
        if 'page_size' in context:
            page_size = context['page_size']
            # Linear scaling for pagination
            thresholds['response_time'] *= (1 + page_size / 100)
            thresholds['memory_usage'] += page_size * 0.5  # ~0.5MB per additional item
            
        if 'include_relations' in context and context['include_relations']:
            # Additional queries and processing for relations
            thresholds['response_time'] *= 1.5
            thresholds['query_count'] += 3
            thresholds['memory_usage'] += 10
            
        if 'search_complexity' in context:
            complexity = context['search_complexity']
            if complexity == 'high':
                thresholds['response_time'] *= 2
                thresholds['query_count'] += 2
                
        return thresholds


@dataclass
class TestExecutionSummary:
    """Comprehensive summary of test execution with insights."""
    total_tests: int
    passed_tests: int
    failed_tests: int
    average_score: float
    grade_distribution: Dict[str, int]
    critical_issues: List[str]
    optimization_opportunities: List[str]
    performance_trends: Dict[str, str]
    execution_time: float
    recommendations: List[str]


class MercuryPerformanceHistory:
    """Performance history tracking and analysis system."""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / "logs" / "mercury_performance.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for performance history."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    test_class TEXT NOT NULL,
                    test_method TEXT NOT NULL,
                    operation_name TEXT NOT NULL,
                    response_time REAL NOT NULL,
                    memory_usage REAL NOT NULL,
                    query_count INTEGER NOT NULL,
                    performance_score REAL NOT NULL,
                    grade TEXT NOT NULL,
                    has_n_plus_one BOOLEAN NOT NULL,
                    context_data TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_baselines (
                    operation_type TEXT PRIMARY KEY,
                    avg_response_time REAL NOT NULL,
                    avg_memory_usage REAL NOT NULL,
                    avg_query_count REAL NOT NULL,
                    sample_count INTEGER NOT NULL,
                    last_updated TEXT NOT NULL
                )
            """)
    
    def store_measurement(self, test_class: str, test_method: str, 
                         metrics: EnhancedPerformanceMetrics_Python,
                         context: Optional[Dict[str, Any]] = None):
        """Store performance measurement in history."""
        from datetime import datetime
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO performance_history 
                (timestamp, test_class, test_method, operation_name, response_time, 
                 memory_usage, query_count, performance_score, grade,
                 has_n_plus_one, context_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                test_class,
                test_method,
                metrics.operation_name,
                metrics.response_time,
                metrics.memory_usage,
                metrics.query_count,
                metrics.performance_score.total_score,
                metrics.performance_score.grade,
                metrics.django_issues.has_n_plus_one,
                json.dumps(context or {})
            ))
    
    def get_baseline(self, operation_type: str) -> Optional[PerformanceBaseline]:
        """Get performance baseline for operation type."""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute("""
                SELECT * FROM performance_baselines WHERE operation_type = ?
            """, (operation_type,)).fetchone()
            
            if result:
                return PerformanceBaseline(
                    operation_type=result[0],
                    avg_response_time=result[1],
                    avg_memory_usage=result[2],
                    avg_query_count=result[3],
                    sample_count=result[4],
                    last_updated=result[5]
                )
        return None
    
    def update_baseline(self, baseline: PerformanceBaseline):
        """Update or create performance baseline."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO performance_baselines
                (operation_type, avg_response_time, avg_memory_usage, avg_query_count,
                sample_count, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                baseline.operation_type,
                baseline.avg_response_time,
                baseline.avg_memory_usage,
                baseline.avg_query_count,
                baseline.sample_count,
                baseline.last_updated
            ))
    
    def detect_regressions(self, test_class: str, test_method: str, 
                          current_metrics: EnhancedPerformanceMetrics_Python) -> List[str]:
        """Detect performance regressions compared to history."""
        regressions = []
        
        with sqlite3.connect(self.db_path) as conn:
            # Get recent historical measurements for this test
            results = conn.execute("""
                SELECT response_time, memory_usage, query_count, performance_score
                FROM performance_history 
                WHERE test_class = ? AND test_method = ?
                ORDER BY timestamp DESC LIMIT 10
            """, (test_class, test_method)).fetchall()
            
            if len(results) >= 3:  # Need some history for meaningful comparison
                historical_times = [r[0] for r in results]
                historical_scores = [r[3] for r in results]
                
                avg_historical_time = sum(historical_times) / len(historical_times)
                avg_historical_score = sum(historical_scores) / len(historical_scores)
                
                # Check for regressions
                if current_metrics.response_time > avg_historical_time * 1.5:
                    regressions.append(f"Response time regression: {current_metrics.response_time:.1f}ms vs historical {avg_historical_time:.1f}ms")
                
                if current_metrics.performance_score.total_score < avg_historical_score - 15:
                    regressions.append(f"Performance score regression: {current_metrics.performance_score.total_score:.1f} vs historical {avg_historical_score:.1f}")
                
                # Check for new N+1 issues
                historical_n_plus_one = conn.execute("""
                    SELECT has_n_plus_one FROM performance_history
                    WHERE test_class = ? AND test_method = ?
                    ORDER BY timestamp DESC LIMIT 5
                """, (test_class, test_method)).fetchall()
                
                if (current_metrics.django_issues.has_n_plus_one and 
                    not any(r[0] for r in historical_n_plus_one)):
                    regressions.append("New N+1 query issue detected")
        
        return regressions


class MercuryThresholdOverride:
    """Context manager for temporarily overriding performance thresholds."""
    
    def __init__(self, test_instance):
        self.test_instance = test_instance
        self.original_thresholds = None
        self.override_thresholds = None
    
    def __call__(self, thresholds: Dict[str, Union[int, float]]):
        """Set the thresholds to override."""
        self.override_thresholds = thresholds
        return self
    
    def __enter__(self):
        """Apply the threshold overrides."""
        self.original_thresholds = self.test_instance._per_test_thresholds
        self.test_instance._per_test_thresholds = self.override_thresholds
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore the original thresholds."""
        self.test_instance._per_test_thresholds = self.original_thresholds


class DjangoMercuryAPITestCase(DjangoPerformanceAPITestCase):
    """
    Intelligent, Self-Managing Django API Performance Test Case
    
    Automatically handles:
    - Performance monitoring for all test methods
    - Smart threshold management based on operation complexity  
    - N+1 detection and optimization guidance
    - Performance scoring and trend analysis
    - Historical baseline tracking
    - Executive summary generation
    """
    
    # Class-level configuration
    _mercury_enabled = True
    _auto_scoring = True
    _auto_threshold_adjustment = True
    _store_history = True
    _generate_summaries = True
    _verbose_reporting = False
    _educational_guidance = True
    _summary_generated = False  # Prevent double printing
    
    # Custom performance thresholds (set by user in setUpClass)
    _custom_thresholds: Optional[Dict[str, Any]] = None
    
    # Per-test threshold overrides (temporary, resets after each test)
    _per_test_thresholds: Optional[Dict[str, Any]] = None
    
    # Class-level tracking
    _test_executions: List[EnhancedPerformanceMetrics_Python] = []
    _test_failures: List[str] = []
    _optimization_recommendations: List[str] = []
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._history = MercuryPerformanceHistory()
        self._operation_profiles = self._initialize_operation_profiles()
        self._test_context: Dict[str, Any] = {}
        
    def setUp(self):
        """Enhanced setup with automatic Mercury initialization."""
        super().setUp()
        
        if self._mercury_enabled:
            print(
                f"{colors.colorize('🚀 Mercury Intelligent Performance Testing', EduLiteColorScheme.ACCENT, bold=True)}")
            print(f"{colors.colorize('🧠 Auto-monitoring enabled | 🎯 Smart thresholds | 📊 Performance scoring', EduLiteColorScheme.INFO)}")
    
    def _initialize_operation_profiles(self) -> Dict[str, OperationProfile]:
        """Initialize smart operation profiles for different API operations with realistic Django defaults."""
        return {
            'list_view': OperationProfile(
                operation_name='list_view',
                expected_query_range=(3, 25),  # More realistic for Django with potential N+1 issues
                response_time_baseline=200,     # More forgiving default
                memory_overhead_tolerance=30,   # Allow for serialization overhead
                complexity_factors={'pagination': True, 'serialization': 'moderate'}
            ),
            'detail_view': OperationProfile(
                operation_name='detail_view', 
                expected_query_range=(1, 10),  # Allow for related model access
                response_time_baseline=150,
                memory_overhead_tolerance=20,
                complexity_factors={'relations': 'optional', 'serialization': 'simple'}
            ),
            'create_view': OperationProfile(
                operation_name='create_view',
                expected_query_range=(2, 15),  # Allow for validation queries and signals
                response_time_baseline=250,
                memory_overhead_tolerance=25,
                complexity_factors={'validation': True, 'signals': True}
            ),
            'update_view': OperationProfile(
                operation_name='update_view',
                expected_query_range=(2, 12),
                response_time_baseline=200,
                memory_overhead_tolerance=20,
                complexity_factors={'validation': True, 'signals': True}
            ),
            'delete_view': OperationProfile(
                operation_name='delete_view',
                expected_query_range=(1, 30),  # DELETE operations naturally require more queries
                response_time_baseline=300,     # Allow more time for cascade deletions
                memory_overhead_tolerance=40,   
                complexity_factors={'cascade_deletions': True, 'foreign_keys': True, 'cleanup': True}
            ),
            'search_view': OperationProfile(
                operation_name='search_view',
                expected_query_range=(1, 30),  # Search can be complex
                response_time_baseline=300,
                memory_overhead_tolerance=40,
                complexity_factors={'filtering': True, 'ordering': True}
            ),
            'authentication': OperationProfile(
                operation_name='authentication',
                expected_query_range=(0, 8),   # Auth can involve several lookups
                response_time_baseline=100,
                memory_overhead_tolerance=15,
                complexity_factors={'security': True}
            )
        }
    
    def _detect_operation_type(self, test_method_name: str, test_function: Callable) -> str:
        """Intelligently detect operation type from test method name and function."""
        method_name = test_method_name.lower()
        
        # Analyze method name patterns - prioritize DELETE detection
        if any(keyword in method_name for keyword in ['delete', 'destroy', 'remove']):
            return 'delete_view'
        elif any(keyword in method_name for keyword in ['list', 'get_all', 'index']):
            return 'list_view'
        elif any(keyword in method_name for keyword in ['detail', 'retrieve', 'get_single']):
            return 'detail_view'
        elif any(keyword in method_name for keyword in ['create', 'post', 'add']):
            return 'create_view'
        elif any(keyword in method_name for keyword in ['update', 'put', 'patch', 'edit']):
            return 'update_view'
        elif any(keyword in method_name for keyword in ['search', 'filter', 'query']):
            return 'search_view'
        
        # Analyze test function for HTTP method patterns - prioritize DELETE detection
        if test_function:
            try:
                source = inspect.getsource(test_function)
                if 'client.delete' in source:
                    return 'delete_view'
                elif 'client.get' in source and any(param in source for param in ['?search=', '?filter=', '?q=']):
                    return 'search_view'
                elif 'client.get' in source and ('/' in source and not 'list' in method_name):
                    return 'detail_view'
                elif 'client.get' in source:
                    return 'list_view'
                elif 'client.post' in source:
                    return 'create_view'
                elif any(method in source for method in ['client.put', 'client.patch']):
                    return 'update_view'
            except (OSError, TypeError):
                # If we can't get source, fall back to method name analysis
                pass
        
        # Smart fallback based on common patterns
        if 'can_' in method_name or 'cannot_' in method_name:
            # Permission/authorization tests - analyze further
            if 'delete' in method_name:
                return 'delete_view'
            elif 'update' in method_name or 'edit' in method_name:
                return 'update_view'
            elif 'create' in method_name or 'add' in method_name:
                return 'create_view'
            else:
                return 'detail_view'  # Most permission tests are about viewing
        
        # Default fallback - be more intelligent
        return 'detail_view'  # Changed from 'list_view' to more neutral default
    
    def _try_extract_threshold_setting(self, test_function: Callable) -> None:
        """Try to extract and execute threshold setting from test method source."""
        try:
            import ast
            import re
            
            # Get the source code of the test function
            source = inspect.getsource(test_function)
            
            # Look for set_test_performance_thresholds call
            pattern = r'self\.set_test_performance_thresholds\(\s*({[^}]+})\s*\)'
            match = re.search(pattern, source)
            
            if match:
                # Extract the threshold dictionary
                threshold_dict_str = match.group(1)
                
                # Safely evaluate the dictionary
                try:
                    # Parse the dictionary string into an AST
                    tree = ast.parse(threshold_dict_str, mode='eval')
                    
                    # Only allow dict literals with string keys and numeric values
                    if isinstance(tree.body, ast.Dict):
                        thresholds = {}
                        for key, value in zip(tree.body.keys, tree.body.values):
                            if isinstance(key, ast.Str) and isinstance(value, (ast.Num, ast.Constant)):
                                key_str = key.s if hasattr(key, 's') else str(key.value)
                                value_num = value.n if hasattr(value, 'n') else value.value
                                thresholds[key_str] = value_num
                        
                        if thresholds:
                            # Set the thresholds
                            self._per_test_thresholds = thresholds
                            
                except (ValueError, SyntaxError, AttributeError):
                    # If parsing fails, ignore and continue
                    pass
                    
        except (OSError, TypeError, ImportError):
            # If we can't get source or parse it, ignore and continue
            pass
    
    def _extract_test_context(self, test_function: Callable) -> Dict[str, Any]:
        """Extract context information from test function for smart threshold adjustment."""
        context = {}
        
        if test_function:
            try:
                source = inspect.getsource(test_function)
                
                # Detect pagination
                if 'page_size' in source:
                    # Try to extract page_size value
                    import re
                    match = re.search(r'page_size[=:](\d+)', source)
                    if match:
                        context['page_size'] = int(match.group(1))
                    else:
                        context['page_size'] = 20  # Default assumption
                
                # Detect relation includes
                if any(keyword in source for keyword in ['select_related', 'prefetch_related', 'include']):
                    context['include_relations'] = True
                
                # Detect search complexity
                if any(keyword in source for keyword in ['search', 'filter', 'Q(']):
                    if any(complex_pattern in source for complex_pattern in ['Q(', '__icontains', '__in']):
                        context['search_complexity'] = 'high'
                    else:
                        context['search_complexity'] = 'medium'
                        
            except Exception:
                pass  # Fallback gracefully if source analysis fails
                
        return context
    
    def _calculate_intelligent_thresholds(self, operation_type: str, context: Dict[str, Any]) -> Dict[str, float]:
        """Calculate intelligent thresholds based on operation type, context, and custom overrides."""
        
        # Priority: per-test overrides > class-wide custom thresholds > intelligent defaults
        if self._per_test_thresholds:
            # Use per-test thresholds directly if provided
            thresholds = {
                'response_time': self._per_test_thresholds.get('response_time_ms', 500),
                'memory_usage': 80 + self._per_test_thresholds.get('memory_overhead_mb', 50),
                'query_count': self._per_test_thresholds.get('query_count_max', 50),
            }
            return thresholds
        elif self._custom_thresholds:
            # Use custom thresholds directly if provided
            thresholds = {
                'response_time': self._custom_thresholds.get('response_time_ms', 500),
                'memory_usage': 80 + self._custom_thresholds.get('memory_overhead_mb', 50),
                'query_count': self._custom_thresholds.get('query_count_max', 50),
            }
            return thresholds
        
        # Get operation profile for defaults
        profile = self._operation_profiles.get(operation_type, self._operation_profiles['list_view'])
        
        # Calculate dynamic thresholds
        thresholds = profile.calculate_dynamic_thresholds(context)
        
        # Adjust based on historical baselines if available
        baseline = self._history.get_baseline(operation_type)
        if baseline and baseline.sample_count >= 5:
            # Use historical data to refine thresholds (with 20% tolerance)
            thresholds['response_time'] = max(thresholds['response_time'], baseline.avg_response_time * 1.2)
            thresholds['memory_usage'] = max(thresholds['memory_usage'], baseline.avg_memory_usage + 10)
            
        return thresholds
    
    def _generate_contextual_recommendations(self, metrics: EnhancedPerformanceMetrics_Python, 
                                           operation_type: str) -> List[str]:
        """Generate contextual optimization recommendations based on operation type and issues."""
        recommendations = []
        
        # Get base recommendations from metrics
        base_recommendations = metrics._get_recommendations()
        recommendations.extend(base_recommendations)
        
        # Add operation-specific recommendations
        if operation_type == 'list_view':
            if metrics.query_count > 5:
                recommendations.append("🔧 List View: Implement select_related() and prefetch_related() for all foreign keys")
                recommendations.append("📄 List View: Consider implementing cursor pagination for large datasets")
            
            if metrics.response_time > 200:
                recommendations.append("⚡ List View: Add database indexes for filtering/ordering fields")
                recommendations.append("💾 List View: Implement caching for frequently accessed list data")
                
        elif operation_type == 'detail_view':
            if metrics.query_count > 3:
                recommendations.append("🔧 Detail View: Use select_related() for all foreign keys in the queryset")
            
            if metrics.memory_overhead > 15:
                recommendations.append("💾 Detail View: Review serializer field selection - consider using 'fields' parameter")
                
        elif operation_type == 'create_view':
            if metrics.query_count > 8:
                recommendations.append("🔧 Create View: Consider optimizing Django signals - use bulk_create() where possible")
                recommendations.append("🔧 Create View: Review post_save signals for unnecessary database queries")
                recommendations.append("🔧 Create View: Consider combining related object creation into fewer transactions")
            
            if metrics.response_time > 300:
                recommendations.append("⚡ Create View: Move heavy signal processing to background tasks (Celery)")
                recommendations.append("⚡ Create View: Consider using select_for_update() to prevent race conditions")
                recommendations.append("⚡ Create View: Cache validation queries (username/email uniqueness)")
            
            if metrics.query_count > 5:
                recommendations.append("🔧 Create View: Consider using get_or_create() instead of separate queries")
                recommendations.append("🔧 Create View: Review serializer validation - combine database lookups")
                
        elif operation_type == 'delete_view':
            if metrics.query_count > 15:
                recommendations.append("🗑️ Delete View: Consider database-level CASCADE constraints for better performance")
            
            if metrics.response_time > 500:
                recommendations.append("🚀 Delete View: Consider implementing soft deletes for complex relationships")
                recommendations.append("📋 Delete View: Queue deletion operations for background processing with Celery")
                
        elif operation_type == 'search_view':
            if metrics.response_time > 300:
                recommendations.append("🔍 Search View: Add database indexes for search fields")
                recommendations.append("🔍 Search View: Consider using full-text search (PostgreSQL) or Elasticsearch")
            
            if metrics.query_count > 10:
                recommendations.append("🔧 Search View: Optimize search querysets with select_related/prefetch_related")
        
        # Add executive-level recommendations for high-impact issues
        if metrics.django_issues.has_n_plus_one:
            severity = metrics.django_issues.n_plus_one_analysis.severity_text
            if severity in ['SEVERE', 'CRITICAL']:
                recommendations.insert(0, "🚨 EXECUTIVE PRIORITY: N+1 query issue will impact production performance significantly")
                recommendations.insert(1, "💼 Business Impact: This issue can cause database overload and slow user experience")
                
        return recommendations
    
    def _auto_wrap_test_method(self, original_method: Callable) -> Callable:
        """Automatically wrap test methods with performance monitoring."""
        
        @wraps(original_method)
        def wrapped_test_method(self_inner):
            if not self._mercury_enabled:
                return original_method(self_inner)
            
            # Detect operation type and context
            operation_type = self._detect_operation_type(original_method.__name__, original_method)
            context = self._extract_test_context(original_method)
            
            # Create operation name
            operation_name = f"{self.__class__.__name__}.{original_method.__name__}"
            
            # Try to extract and execute threshold setting from test method
            self_inner._try_extract_threshold_setting(original_method)
            
            # Calculate thresholds now that per-test thresholds might be set
            context['max_response_time'] = self._per_test_thresholds.get('response_time_ms', 500) if self._per_test_thresholds else 500
            thresholds = self._calculate_intelligent_thresholds(operation_type, context) if self._auto_threshold_adjustment else {}
            
            # Set up monitoring
            def test_function():
                return original_method(self_inner)
            
            test_executed = False
            metrics = None
            response_time = None
            
            try:
                # Run comprehensive analysis with intelligent settings, but catch threshold failures
                start_time = time.perf_counter()
                try:
                    
                    metrics: EnhancedPerformanceMetrics_Python = self_inner.run_comprehensive_analysis(
                        operation_name=operation_name,
                        test_function=test_function,
                        operation_type=operation_type,
                        expect_response_under=thresholds.get('response_time'),
                        expect_memory_under=thresholds.get('memory_usage'), 
                        expect_queries_under=thresholds.get('query_count'),
                        print_analysis=self._verbose_reporting,
                        show_scoring=self._auto_scoring,
                        auto_detect_n_plus_one=True
                    )
                    test_executed = True
                    context['response_time'] = metrics.response_time # directly from monitor
                except Exception as monitor_exception:
                    response_time = (time.perf_counter() - start_time) * 1000 # from python time (monitor failed)
                    context['response_time'] = response_time 
                    # If the monitor failed, we still want to capture metrics if they exist
                    # Try to get metrics from the monitor even if it threw an exception
                    if "Performance thresholds exceeded" in str(monitor_exception):
                        # This is likely a threshold failure, try to extract metrics from the monitor
                        # We'll catch the exception and re-raise it after tracking
                        test_executed = True
                        raise monitor_exception
                    else:
                        # Some other error, re-raise immediately
                        raise
                
            except Exception as e:
                error_msg = str(e)
                
                # Provide educational guidance for threshold failures
                if "Performance thresholds exceeded" in error_msg and self._educational_guidance:
                    context['message'] = f"Exceded {context['max_response_time']}ms by {round(context['response_time'] - context['max_response_time'], 2)}ms"
                    self_inner._provide_threshold_guidance(original_method.__name__, error_msg, operation_type, context)
                
                self_inner._test_failures.append(f"❌ {original_method.__name__}: {error_msg}")
                
                # For threshold failures, we might still be able to get metrics
                # Let's try to run the test function directly with monitoring to get metrics
                if "Performance thresholds exceeded" in error_msg and test_executed:
                    try:
                        # Run without thresholds to get metrics
                        monitor = self_inner.monitor_django_view(f"{operation_name}.metrics_only")
                        with monitor:
                            test_function()
                        metrics = monitor.metrics
                    except:
                        # If this fails too, we can't get metrics
                        pass
                
                # Always re-raise to fail the test
                raise
                
            finally:
                # Always track execution if we got metrics (even if test failed)
                if test_executed and metrics:
                    # Store in history if enabled
                    if self._store_history:
                        self_inner._history.store_measurement(
                            test_class=self.__class__.__name__,
                            test_method=original_method.__name__,
                            metrics=metrics,
                            context=context
                        )
                    
                    # Update baselines
                    baseline = self_inner._history.get_baseline(operation_type)
                    if baseline:
                        baseline.update_with_new_measurement(metrics)
                    else:
                        from datetime import datetime
                        baseline = PerformanceBaseline(
                            operation_type=operation_type,
                            avg_response_time=metrics.response_time,
                            avg_memory_usage=metrics.memory_usage,
                            avg_query_count=metrics.query_count,
                            sample_count=1,
                            last_updated=datetime.now().isoformat()
                        )
                    self_inner._history.update_baseline(baseline)
                    
                    # Detect regressions
                    regressions = self_inner._history.detect_regressions(
                        test_class=self.__class__.__name__,
                        test_method=original_method.__name__,
                        current_metrics=metrics
                    )
                    
                    if regressions:
                        for regression in regressions:
                            self_inner._test_failures.append(f"📉 {original_method.__name__}: {regression}")
                    
                    # Generate contextual recommendations
                    recommendations = self_inner._generate_contextual_recommendations(metrics, operation_type)
                    self_inner._optimization_recommendations.extend(recommendations)
                    
                    # ALWAYS track execution for summary (even if test failed)
                    self_inner._test_executions.append(metrics)
                    
                    # Show intelligent summary
                    if not self._verbose_reporting:
                        grade_color = {
                            'S': EduLiteColorScheme.EXCELLENT,
                            'A+': EduLiteColorScheme.EXCELLENT,
                            'A': EduLiteColorScheme.GOOD,
                            'B': EduLiteColorScheme.ACCEPTABLE,
                            'C': EduLiteColorScheme.WARNING,
                            'D': EduLiteColorScheme.CRITICAL,
                            'F': EduLiteColorScheme.CRITICAL
                        }.get(metrics.performance_score.grade, EduLiteColorScheme.TEXT)
                        
                        print(f"   🎯 {colors.colorize(f'{original_method.__name__}', EduLiteColorScheme.INFO)}: "
                              f"{colors.colorize(f'Grade {metrics.performance_score.grade}', grade_color, bold=True)} "
                              f"({metrics.response_time:.1f}ms, {metrics.query_count}Q, "
                              f"{metrics.memory_overhead:.1f}MB overhead)")
                        
                        # Show critical issues immediately - only if severity > 0
                        if metrics.django_issues.has_n_plus_one and metrics.django_issues.n_plus_one_analysis.severity_level > 0:
                            analysis = metrics.django_issues.n_plus_one_analysis
                            print(f"      🚨 {colors.colorize(f'N+1 Issue: {analysis.severity_text}', EduLiteColorScheme.CRITICAL)}")
                
                # Reset per-test thresholds after each test
                self_inner._per_test_thresholds = None
                
            return metrics
        
        return wrapped_test_method
    
    def _provide_threshold_guidance(self, test_name: str, error_msg: str, operation_type: str, context: Dict[str, Any]):
        """Provide educational guidance when default thresholds are exceeded."""
        print(f"\n{colors.colorize('📚 MERCURY EDUCATIONAL GUIDANCE', EduLiteColorScheme.OPTIMIZATION, bold=True)}")
        print(f"{colors.colorize('=' * 60, EduLiteColorScheme.BORDER)}")
        
        print(f"🎯 {colors.colorize(f'Test: {test_name}', EduLiteColorScheme.INFO)}")
        print(f"⚠️  {colors.colorize('Default thresholds exceeded', EduLiteColorScheme.WARNING)}")
        print(f"🔍 {colors.colorize(f'Operation Type: {operation_type}', EduLiteColorScheme.INFO)}")
        
        # Extract specific failure details with operation-specific context
        if "Query count" in error_msg:
            print(f"\n💡 {colors.colorize('SOLUTION: Configure Custom Query Thresholds', EduLiteColorScheme.OPTIMIZATION, bold=True)}")
            if operation_type == 'delete_view':
                print(f"   DELETE operations naturally require more database queries due to:")
                print(f"   • CASCADE relationships (UserProfile -> User)")
                print(f"   • Foreign key cleanup (ProfileFriendRequest references)")
                print(f"   • Many-to-many cleanup (friends relationship)")
                print(f"   • Related model cleanup (privacy settings, notifications)")
                print(f"   This is expected behavior for models with complex relationships.")
            elif operation_type == 'create_view':
                print(f"   CREATE operations with complex models often require more database queries due to:")
                print(f"   • Django signals creating related objects (post_save → UserProfile → UserProfilePrivacySettings)")
                print(f"   • Validation queries (email uniqueness, username uniqueness)")
                print(f"   • Transaction handling across multiple models")
                print(f"   • Many-to-many field initialization")
                print(f"   This is normal behavior for registration/creation endpoints with signals.")
            else:
                print(f"   Your API is making more database queries than Mercury's default expectations.")
                print(f"   This often indicates N+1 query issues that should be fixed, but you can")
                print(f"   also set custom thresholds while you work on optimization.")
        
        if "Response time" in error_msg:
            if operation_type == 'delete_view':
                print(f"   DELETE operations typically take longer due to cascade cleanup operations.")
            elif operation_type == 'create_view':
                print(f"   CREATE operations may take longer due to:")
                print(f"   • Django signal processing (creating related UserProfile and privacy settings)")
                print(f"   • Database validation queries (uniqueness checks for email/username)")
                print(f"   • Transaction commits across multiple tables")
                print(f"   • Password hashing and user creation logic")
                print(f"   {colors.colorize(context['message'], EduLiteColorScheme.FADE)}")
            else:
                print(f"   Your API is taking longer than Mercury's default expectations. {colors.colorize(context['message'], EduLiteColorScheme.FADE)}")
        
        print(f"\n{colors.colorize('🛠️  How to Configure Custom Thresholds:', EduLiteColorScheme.ACCENT, bold=True)}")
        
        # Provide operation-specific threshold suggestions
        print(f"""
    Add this to your test class setUpClass method:

    {colors.colorize("@classmethod", EduLiteColorScheme.FADE)}
    {colors.colorize("def", EduLiteColorScheme.BACKGROUND)} {colors.colorize("setUpClass", EduLiteColorScheme.QUERY_ACCEPTABLE)}({colors.colorize("cls", EduLiteColorScheme.ACCENT)}):
        {colors.colorize("super()", EduLiteColorScheme.ACCENT)}.setUpClass()
        
        {colors.colorize("# Configure custom performance thresholds", EduLiteColorScheme.FADE)}
        {colors.colorize("cls", EduLiteColorScheme.ACCENT)}.{colors.colorize("set_performance_thresholds", EduLiteColorScheme.OPTIMIZATION)}({{
            '{colors.colorize("response_time_ms", EduLiteColorScheme.QUERY_PROBLEMATIC)}': 500,      {colors.colorize("# Allow up to 500ms response time", EduLiteColorScheme.FADE)}
            '{colors.colorize("query_count_max", EduLiteColorScheme.QUERY_PROBLEMATIC)}': 30,        {colors.colorize("# Allow up to 30 database queries", EduLiteColorScheme.FADE)}
            '{colors.colorize("memory_overhead_mb", EduLiteColorScheme.QUERY_PROBLEMATIC)}': 50,     {colors.colorize("# Allow up to 50MB memory overhead", EduLiteColorScheme.FADE)}
        }})

        {colors.colorize("# Configure Mercury for this test suite", EduLiteColorScheme.FADE)}
        {colors.colorize("cls", EduLiteColorScheme.ACCENT)}.{colors.colorize("configure_mercury", EduLiteColorScheme.OPTIMIZATION)}(
            {colors.colorize("enabled", EduLiteColorScheme.QUERY_PROBLEMATIC)}=True, {colors.colorize("auto_scoring", EduLiteColorScheme.QUERY_PROBLEMATIC)}=True, {colors.colorize("auto_threshold_adjustment", EduLiteColorScheme.QUERY_PROBLEMATIC)}=True,
            {colors.colorize("store_history", EduLiteColorScheme.QUERY_PROBLEMATIC)}=True, {colors.colorize("verbose_reporting", EduLiteColorScheme.QUERY_PROBLEMATIC)}=False, {colors.colorize("generate_summaries", EduLiteColorScheme.QUERY_PROBLEMATIC)}=True,
            {colors.colorize("educational_guidance", EduLiteColorScheme.QUERY_PROBLEMATIC)}=True {colors.colorize("# Set to False to disable messages like this", EduLiteColorScheme.FADE)}
            )
        
    {colors.colorize("# Optionally, set custom thresholds for individual tests", EduLiteColorScheme.FADE)}
    {colors.colorize("def", EduLiteColorScheme.BACKGROUND)} {colors.colorize("test_something", EduLiteColorScheme.QUERY_ACCEPTABLE)}({colors.colorize("self", EduLiteColorScheme.ACCENT)}):
        {colors.colorize("self", EduLiteColorScheme.ACCENT)}.{colors.colorize("set_test_performance_thresholds", EduLiteColorScheme.OPTIMIZATION)}({{ 
            '{colors.colorize("response_time_ms", EduLiteColorScheme.QUERY_PROBLEMATIC)}': 1000,      {colors.colorize("# Allow up to 1000ms response time", EduLiteColorScheme.FADE)}
            '{colors.colorize("query_count_max", EduLiteColorScheme.QUERY_PROBLEMATIC)}': 50,        {colors.colorize("# Allow up to 50 database queries", EduLiteColorScheme.FADE)}
            '{colors.colorize("memory_overhead_mb", EduLiteColorScheme.QUERY_PROBLEMATIC)}': 120,     {colors.colorize("# Allow up to 120MB memory overhead", EduLiteColorScheme.FADE)}
        }})
    
        {colors.colorize("# Your existing test code...", EduLiteColorScheme.FADE)}
        """)
        

        
        print(f"\n{colors.colorize('=' * 60, EduLiteColorScheme.BORDER)}")
    
    @classmethod
    def set_performance_thresholds(cls, thresholds: Dict[str, Union[int, float]]):
        """
        Set custom performance thresholds for all tests in this class.
        
        Args:
            thresholds: Dictionary with keys:
                - response_time_ms: Maximum response time in milliseconds
                - query_count_max: Maximum number of database queries  
                - memory_overhead_mb: Maximum memory overhead in MB
                
        Example:
            cls.set_performance_thresholds({
                'response_time_ms': 300,
                'query_count_max': 15,
                'memory_overhead_mb': 40,
            })
        """
        cls._custom_thresholds = thresholds
        print(f"🎯 {colors.colorize('Custom performance thresholds configured', EduLiteColorScheme.SUCCESS)}")
        for key, value in thresholds.items():
            unit = 'ms' if 'time' in key else 'MB' if 'memory' in key else '%' if 'efficiency' in key else ''
            print(f"   • {key}: {value}{unit}")
    
    def set_test_performance_thresholds(self, thresholds: Dict[str, Union[int, float]]):
        """
        Set custom performance thresholds for the current test only.
        These thresholds override class-wide thresholds for this test only.
        After the test completes, thresholds revert to class-wide configuration.
        
        Args:
            thresholds: Dictionary with keys:
                - response_time_ms: Maximum response time in milliseconds
                - query_count_max: Maximum number of database queries  
                - memory_overhead_mb: Maximum memory overhead in MB
                
        Example:
            def test_expensive_operation(self):
                # Allow higher thresholds for this specific test
                self.set_test_performance_thresholds({
                    'response_time_ms': 1000,  # Allow 1 second for this test
                    'query_count_max': 50,     # Allow more queries
                })
                
                response = self.client.get('/api/expensive-operation/')
                self.assertEqual(response.status_code, 200)
        """
        self._per_test_thresholds = thresholds
        print(f"⚡ {colors.colorize('Per-test performance thresholds set', EduLiteColorScheme.OPTIMIZATION)}")
        for key, value in thresholds.items():
            unit = 'ms' if 'time' in key else 'MB' if 'memory' in key else '%' if 'efficiency' in key else ''
            print(f"   • {key}: {value}{unit} (this test only)")
    
    @property
    def mercury_override_thresholds(self):
        """
        Context manager for temporarily overriding performance thresholds.
        
        Example:
            def test_something(self):
                with self.mercury_override_thresholds({'query_count_max': 50}):
                    # Code that might need more queries
                    response = self.client.get('/api/complex-endpoint/')
                    self.assertEqual(response.status_code, 200)
        """
        return MercuryThresholdOverride(self)
    
    def __new__(cls, *args, **kwargs):
        """Auto-wrap test methods with Mercury monitoring."""
        instance = super().__new__(cls)
        
        # Auto-wrap all test methods
        for attr_name in dir(cls):
            if attr_name.startswith('test_') and callable(getattr(cls, attr_name)):
                original_method = getattr(cls, attr_name)
                if not hasattr(original_method, '_mercury_wrapped'):
                    wrapped_method = instance._auto_wrap_test_method(original_method)
                    wrapped_method._mercury_wrapped = True
                    setattr(instance, attr_name, wrapped_method.__get__(instance, cls))
        
        return instance
    
    @classmethod
    def tearDownClass(cls):
        """Generate comprehensive Mercury performance summary."""
        super().tearDownClass()
        
        if not cls._mercury_enabled or not cls._test_executions or cls._summary_generated:
            return
        
        cls._summary_generated = True  # Prevent double printing
        cls._generate_mercury_executive_summary()
    
    @classmethod
    def _generate_mercury_executive_summary(cls):
        """Generate comprehensive executive summary with actionable insights."""
        
        # Create enhanced dashboard for the test suite
        cls._create_mercury_dashboard()
        
        print(f"\n{colors.colorize('🎯 MERCURY INTELLIGENT PERFORMANCE ANALYSIS', EduLiteColorScheme.ACCENT, bold=True)}")
        print(f"{colors.colorize('=' * 80, EduLiteColorScheme.BORDER)}")
        
        if not cls._test_executions:
            print(f"{colors.colorize('No performance data collected.', EduLiteColorScheme.WARNING)}")
            return
        
        # Calculate aggregate statistics  
        total_tests = len(cls._test_executions)
        scores = [m.performance_score.total_score for m in cls._test_executions]
        grades = [m.performance_score.grade for m in cls._test_executions]
        
        avg_score = sum(scores) / len(scores)
        avg_response_time = sum(m.response_time for m in cls._test_executions) / total_tests
        avg_query_count = sum(m.query_count for m in cls._test_executions) / total_tests
        
        # Grade distribution
        from collections import Counter
        grade_counts = Counter(grades)
        
        # Critical issues analysis
        n_plus_one_tests = sum(1 for m in cls._test_executions 
                             if m.django_issues.has_n_plus_one and 
                             m.django_issues.n_plus_one_analysis.severity_level > 0)
        critical_issues = []
        
        if n_plus_one_tests > 0:
            critical_issues.append(f"N+1 Query Issues: {n_plus_one_tests}/{total_tests} tests affected")
        
        slow_tests = sum(1 for m in cls._test_executions if m.response_time > 300)
        if slow_tests > 0:
            critical_issues.append(f"Slow Response Times: {slow_tests}/{total_tests} tests over 300ms")
        
        # Grade distribution
        print(f"\n📊 {colors.colorize('GRADE DISTRIBUTION', EduLiteColorScheme.INFO, bold=True)}")
        for grade in ['S', 'A+', 'A', 'B', 'C', 'D', 'F']:
            count = grade_counts.get(grade, 0)
            if count > 0:
                percentage = (count / total_tests) * 100
                grade_color = {
                    'S': EduLiteColorScheme.EXCELLENT,
                    'A+': EduLiteColorScheme.EXCELLENT,
                    'A': EduLiteColorScheme.GOOD,
                    'B': EduLiteColorScheme.ACCEPTABLE,
                    'C': EduLiteColorScheme.WARNING,
                    'D': EduLiteColorScheme.CRITICAL,
                    'F': EduLiteColorScheme.CRITICAL
                }.get(grade, EduLiteColorScheme.TEXT)
                
                print(f"   {colors.colorize(f'{grade}: {count} tests ({percentage:.1f}%)', grade_color)}")
        
        # Critical issues
        if critical_issues:
            print(f"\n🚨 {colors.colorize('CRITICAL ISSUES', EduLiteColorScheme.CRITICAL, bold=True)}")
            for issue in critical_issues:
                print(f"   • {colors.colorize(issue, EduLiteColorScheme.CRITICAL)}")
        
        # Test failures
        if cls._test_failures:
            print(f"\n⚠️  {colors.colorize('REGRESSIONS & ISSUES', EduLiteColorScheme.WARNING, bold=True)}")
            for failure in cls._test_failures[:5]:  # Show first 5
                print(f"   • {colors.colorize(failure, EduLiteColorScheme.WARNING)}")
            
            if len(cls._test_failures) > 5:
                print(f"   • {colors.colorize(f'... and {len(cls._test_failures) - 5} more issues', EduLiteColorScheme.FADE)}")
        
        # Top optimization opportunities
        if cls._optimization_recommendations:
            print(f"\n💡 {colors.colorize('TOP OPTIMIZATION OPPORTUNITIES', EduLiteColorScheme.OPTIMIZATION, bold=True)}")
            
            # Prioritize recommendations by impact and remove duplicates more aggressively
            recommendations = list(set(cls._optimization_recommendations))  # Remove exact duplicates
            
            # Remove similar/redundant recommendations
            unique_recs = []
            seen_keywords = set()
            for rec in recommendations:
                # Check if we've already seen a similar recommendation
                rec_keywords = set(rec.lower().split())
                if not any(keyword in seen_keywords for keyword in rec_keywords):
                    unique_recs.append(rec)
                    seen_keywords.update(rec_keywords)
            
            priority_keywords = ['URGENT', 'EXECUTIVE PRIORITY', 'Business Impact', 'N+1']
            
            priority_recs = [r for r in unique_recs if any(keyword in r for keyword in priority_keywords)]
            other_recs = [r for r in unique_recs if not any(keyword in r for keyword in priority_keywords)]
            
            # Show priority recommendations first - limit to avoid spam
            for rec in priority_recs[:2]:  # Reduced from 3 to 2
                print(f"   🔥 {colors.colorize(rec, EduLiteColorScheme.CRITICAL)}")
            
            for rec in other_recs[:3]:  # Reduced from 5 to 3
                print(f"   • {colors.colorize(rec, EduLiteColorScheme.OPTIMIZATION)}")
        
        # Potential improvements
        cls._show_optimization_potential()
        
        # Executive summary
        print(f"\n💼 {colors.colorize('EXECUTIVE SUMMARY', EduLiteColorScheme.ACCENT, bold=True)}")
        
        if avg_score >= 80:
            print(f"   ✅ {colors.colorize('Performance is generally acceptable for production', EduLiteColorScheme.SUCCESS)}")
        elif avg_score >= 60:
            print(f"   ⚠️  {colors.colorize('Performance needs optimization before production', EduLiteColorScheme.WARNING)}")
        else:
            print(f"   🚨 {colors.colorize('Critical performance issues must be addressed', EduLiteColorScheme.CRITICAL)}")
        
        if n_plus_one_tests > total_tests * 0.3:
            print(f"   🔥 {colors.colorize('N+1 query issues are affecting multiple endpoints', EduLiteColorScheme.CRITICAL)}")
            print(f"   💼 {colors.colorize('Business Impact: Database load will increase significantly with user growth', EduLiteColorScheme.WARNING)}")
        
        print(f"\n{colors.colorize('Mercury Analysis Complete - Performance Intelligence Enabled', EduLiteColorScheme.ACCENT, bold=True)}")
        print(f"{colors.colorize('=' * 80, EduLiteColorScheme.BORDER)}")
    
    @classmethod
    def _calculate_overall_grade(cls, avg_score: float) -> str:
        """Calculate overall grade from average score."""
        if avg_score >= 95:
            return "S"
        elif avg_score >= 90:
            return "A+"
        elif avg_score >= 80:
            return "A"
        elif avg_score >= 70:
            return "B"
        elif avg_score >= 60:
            return "C"
        elif avg_score >= 50:
            return "D"
        else:
            return "F"
    
    @classmethod
    def _show_optimization_potential(cls):
        """Show potential score improvements if issues are fixed."""
        if not cls._test_executions:
            return
            
        n_plus_one_tests = [m for m in cls._test_executions if m.django_issues.has_n_plus_one]
        
        if n_plus_one_tests:
            current_avg = sum(m.performance_score.total_score for m in cls._test_executions) / len(cls._test_executions)
            
            # Calculate potential improvement
            potential_scores = []
            for m in cls._test_executions:
                if m.django_issues.has_n_plus_one:
                    potential_score = min(100, m.performance_score.total_score + m.performance_score.n_plus_one_penalty)
                    potential_scores.append(potential_score)
                else:
                    potential_scores.append(m.performance_score.total_score)
            
            potential_avg = sum(potential_scores) / len(potential_scores)
            improvement = potential_avg - current_avg
            
            print(f"\n🚀 {colors.colorize('OPTIMIZATION POTENTIAL', EduLiteColorScheme.OPTIMIZATION, bold=True)}")
            print(f"   📈 Current Average Score: {current_avg:.1f}/100")
            print(f"   🎯 Potential Score (N+1 fixed): {potential_avg:.1f}/100")
            print(f"   ⬆️  Improvement: +{improvement:.1f} points")
            
            potential_grade = cls._calculate_overall_grade(potential_avg)
            print(f"   🏆 Potential Grade: {colors.colorize(potential_grade, EduLiteColorScheme.EXCELLENT, bold=True)}")
    
    @classmethod
    def _create_mercury_dashboard(cls):
        """Create enhanced dashboard for Mercury test suite summary."""
        if not cls._test_executions:
            return
        
        # Calculate aggregate metrics
        total_tests = len(cls._test_executions)
        avg_response_time = sum(m.response_time for m in cls._test_executions) / total_tests
        avg_memory_usage = sum(m.memory_usage for m in cls._test_executions) / total_tests
        total_queries = sum(m.query_count for m in cls._test_executions)
        avg_query_count = total_queries / total_tests
        
        # Calculate overall scores
        scores = [m.performance_score.total_score for m in cls._test_executions]
        avg_score = sum(scores) / len(scores)
        overall_grade = cls._calculate_overall_grade(avg_score)
        
        # Critical issues count
        n_plus_one_count = sum(1 for m in cls._test_executions 
                             if m.django_issues.has_n_plus_one and 
                             m.django_issues.n_plus_one_analysis.severity_level > 0)
        slow_tests = sum(1 for m in cls._test_executions if m.response_time > 300)
        
        # Format performance status
        if avg_score >= 90:
            status = "EXCELLENT"
            status_color = EduLiteColorScheme.EXCELLENT
        elif avg_score >= 80:
            status = "GOOD"
            status_color = EduLiteColorScheme.GOOD
        elif avg_score >= 60:
            status = "ACCEPTABLE"
            status_color = EduLiteColorScheme.ACCEPTABLE
        else:
            status = "NEEDS IMPROVEMENT"
            status_color = EduLiteColorScheme.CRITICAL
        
        # Create dashboard
        print(f"\n{colors.colorize(f'🎨 MERCURY PERFORMANCE DASHBOARD - {cls.__name__}', EduLiteColorScheme.ACCENT, bold=True)}")
        print(f"{colors.colorize('╭─────────────────────────────────────────────────────────────╮', EduLiteColorScheme.BORDER)}")
        print(f"{colors.colorize('│', EduLiteColorScheme.BORDER)} {colors.colorize('🚀 Overall Status:', EduLiteColorScheme.TEXT, bold=True)} {colors.colorize(status, status_color, bold=True):<20} {colors.colorize('│', EduLiteColorScheme.BORDER)}")
        print(f"{colors.colorize('│', EduLiteColorScheme.BORDER)} {colors.colorize('🎓 Overall Grade:', EduLiteColorScheme.TEXT)} {colors.colorize(f'{overall_grade} ({avg_score:.1f}/100)', status_color, bold=True):<25} {colors.colorize('│', EduLiteColorScheme.BORDER)}")
        print(f"{colors.colorize('│', EduLiteColorScheme.BORDER)} {colors.colorize('📊 Tests Executed:', EduLiteColorScheme.TEXT)} {total_tests:<25} {colors.colorize('│', EduLiteColorScheme.BORDER)}")
        print(f"{colors.colorize('│', EduLiteColorScheme.BORDER)} {colors.colorize('⏱️  Avg Response Time:', EduLiteColorScheme.TEXT)} {avg_response_time:.1f}ms{'':<20} {colors.colorize('│', EduLiteColorScheme.BORDER)}")
        print(f"{colors.colorize('│', EduLiteColorScheme.BORDER)} {colors.colorize('🧠 Avg Memory Usage:', EduLiteColorScheme.TEXT)} {avg_memory_usage:.1f}MB{'':<20} {colors.colorize('│', EduLiteColorScheme.BORDER)}")
        print(f"{colors.colorize('│', EduLiteColorScheme.BORDER)} {colors.colorize('🗃️  Total Queries:', EduLiteColorScheme.TEXT)} {total_queries} ({avg_query_count:.1f} avg){'':<10} {colors.colorize('│', EduLiteColorScheme.BORDER)}")
        
        if n_plus_one_count > 0:
            print(f"{colors.colorize('│', EduLiteColorScheme.BORDER)} {colors.colorize('🚨 N+1 Issues:', EduLiteColorScheme.CRITICAL)} {n_plus_one_count}/{total_tests} tests affected{'':<10} {colors.colorize('│', EduLiteColorScheme.BORDER)}")
        
        if slow_tests > 0:
            print(f"{colors.colorize('│', EduLiteColorScheme.BORDER)} {colors.colorize('⏳ Slow Tests:', EduLiteColorScheme.WARNING)} {slow_tests}/{total_tests} over 300ms{'':<12} {colors.colorize('│', EduLiteColorScheme.BORDER)}")
        
        print(f"{colors.colorize('╰─────────────────────────────────────────────────────────────╯', EduLiteColorScheme.BORDER)}")
    
    # Configuration methods for easy customization
    @classmethod
    def configure_mercury(cls, 
                         enabled: bool = True,
                         auto_scoring: bool = True,
                         auto_threshold_adjustment: bool = True,
                         store_history: bool = True,
                         generate_summaries: bool = True,
                         verbose_reporting: bool = False,
                         educational_guidance: bool = True):
        """Configure Mercury behavior for the test class."""
        cls._mercury_enabled = enabled
        cls._auto_scoring = auto_scoring
        cls._auto_threshold_adjustment = auto_threshold_adjustment
        cls._store_history = store_history
        cls._generate_summaries = generate_summaries
        cls._verbose_reporting = verbose_reporting
        cls._educational_guidance = educational_guidance
        
        # Reset tracking variables for fresh test run
        cls._test_executions = []
        cls._test_failures = []
        cls._optimization_recommendations = []
        cls._summary_generated = False
    
    # Convenience methods that maintain backward compatibility
    def assert_mercury_performance_excellent(self, metrics: EnhancedPerformanceMetrics_Python):
        """Assert that performance meets excellent standards (Grade A or above)."""
        self.assertGreaterEqual(metrics.performance_score.total_score, 80,
                               f"Performance score {metrics.performance_score.total_score:.1f} below excellent threshold (80)")
        self.assertLess(metrics.response_time, 100, "Response time should be under 100ms for excellent performance")
        self.assertFalse(metrics.django_issues.has_n_plus_one, "N+1 queries prevent excellent performance")
    
    def assert_mercury_performance_production_ready(self, metrics: EnhancedPerformanceMetrics_Python):
        """Assert that performance is ready for production deployment."""
        self.assertGreaterEqual(metrics.performance_score.total_score, 60,
                               f"Performance score {metrics.performance_score.total_score:.1f} below production threshold (60)")
        self.assertLess(metrics.response_time, 300, "Response time should be under 300ms for production")
        
        if metrics.django_issues.has_n_plus_one:
            severity = metrics.django_issues.n_plus_one_analysis.severity_level
            self.assertLess(severity, 4, f"N+1 severity {severity} too high for production (must be < 4)")