# Test Suite Rebuild & Performance Framework

## Summary

This PR completely rebuilds our test architecture and introduces Mercury, a performance testing framework that caught and fixed a 122-query N+1 issue in UserSearchView.

### New Library Added

https://github.com/80-20-Human-In-The-Loop/Django-Mercury-Performance-Testing

```sh
pip install django-mercury-performance
```

https://github.com/80-20-Human-In-The-Loop/Django-Mercury-Performance-Testing/wiki/Quick-Start

Added to requirements.txt:

```sh
django-mercury-performance==0.0.4
```

Added to settings.py:

```python
# Educational Test Runner via django-mercury-performance
if '--edu' in sys.argv:
    TEST_RUNNER = 'django_mercury.test_runner.EducationalTestRunner'
    # Remove --edu from argv so Django doesn't complain
    sys.argv.remove('--edu')
```

The `--edu` optional flag can be run in `python manage.py test --edu` for an interactive and educational experience through each failing test.

TODO: Feature Yet to be Implemented

## Reworked Test Suite for Users

The test suite for users has been split up into a modular structure. This allows for rapid testing of specific modules, to not waste time waiting on the whole project's test suite when you just need to check one part.

```sh
python manage.py test users.tests.logic
python manage.py test users.tests.views
python manage.py test users.tests.models
python manage.py test users.tests.serializers
python manage.py test users.tests.management
python manage.py test users.tests.integration
python manage.py test users.tests.performance
```

## Performance Testing


Most tests that utilize these new classes are imported like:

```python
# Import Mercury performance testing framework from PyPI package
try:
    from django_mercury import DjangoMercuryAPITestCase
    # Mercury inherits from TransactionTestCase so fixtures work properly
    MERCURY_AVAILABLE = True
except ImportError as e:
    print(f"Mercury framework not available: {e}")
    # Fallback to TransactionTestCase for fixtures
    from django.test import TransactionTestCase as DjangoMercuryAPITestCase
    MERCURY_AVAILABLE = False
```

This is mainly for my own testing purposes while making the library, so you should be able to simply import like:


### users/tests/performance/mercury_demo.py

```python
from django_mecury import DjangoMercuryAPITestCase
```

```python
lass MercuryFrameworkDemo(DjangoMercuryAPITestCase):
    """
    Simple demonstration that Mercury performance framework is working.
    
    Shows Mercury's capabilities:
    - Automatic performance monitoring
    - Intelligent threshold management  
    - Performance scoring with letter grades
    - Educational guidance for optimization
    """
    
    @classmethod
    def setUpClass(cls):
        """Configure Mercury framework for demonstration."""
        super().setUpClass()
        
        if MERCURY_AVAILABLE:
            print("🚀 Initializing Mercury Performance Framework Demo...")
            try:
                cls.configure_mercury(
                    enabled=True,
                    auto_scoring=True,
                    verbose_reporting=True,        # Enable detailed output
                    educational_guidance=True,     # Show optimization tips
                )
                
                # Set demonstration thresholds
                cls.set_performance_thresholds({
                    'response_time_ms': 100,      # Quick response expected
                    'query_count_max': 3,         # Minimal queries for simple test
                    'memory_overhead_mb': 20,     # Low memory overhead
                })
                print("✅ Mercury framework configured successfully!")
            except Exception as e:
                print(f"⚠️ Mercury initialization issue: {e}")
        else:
            print("ℹ️ Mercury framework not available - running basic test")
```

This test file was purposely named without the `test_` prefix, because I only want to show it if you choose to see it via:

```sh
python manage.py test users.tests.performance.mercury_demo
```

![Terminal Image, first part of response](https://i.imgur.com/EIu5ih3.png)

### users/tests/test_user_search.py


```python
def test_admin_user_search_performance(self):
        """Test search performance for admin users."""
        # Create users with varying privacy settings
        self.create_test_users_with_relationships(50)
        
        if MERCURY_AVAILABLE:
            # Monitor admin search
            with monitor_django_view("admin_search") as monitor:
                response = self.admin_client.get('/api/users/search/?q=perf_user')
            
            # Functional assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Admin should see more results than regular users
            admin_results = len(response.data['results'])
            
            # Compare with regular user results
            regular_response = self.authenticated_client.get('/api/users/search/?q=perf_user')
            regular_results = len(regular_response.data['results'])
            
            self.assertGreaterEqual(admin_results, regular_results)
            
            # Performance assertions
            self.assertResponseTimeLess(monitor.metrics, 50, "Admin search should be fast")
            self.assertQueriesLess(monitor.metrics, 5, "Admin search should be optimized")
            self.assertMemoryLess(monitor.metrics, 150, "Should use reasonable memory")
        else:
            response = self.admin_client.get('/api/users/search/?q=perf_user')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            admin_results = len(response.data['results'])
            regular_response = self.authenticated_client.get('/api/users/search/?q=perf_user')
            regular_results = len(regular_response.data['results'])
            self.assertGreaterEqual(admin_results, regular_results)
```

Here is an example failure when we set the response time test to 5ms, an unrealistic expectation:

```sh
FAIL: test_admin_user_search_performance (users.tests.performance.test_user_search.UserSearchPerformanceTest)
Test search performance for admin users.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/mathew/python-3.10.12-Projects/EduLite/backend/EduLite/users/tests/performance/test_user_search.py", line 274, in test_admin_user_search_performance
    self.assertResponseTimeLess(monitor.metrics, 5, "Admin search should be fast")
  File "/home/mathew/.local/lib/python3.10/site-packages/django_mercury/python_bindings/django_integration.py", line 94, in assertResponseTimeLess
    self.fail(
AssertionError: Admin search should be fast: Response time 8.03ms is not less than 5ms

----------------------------------------------------------------------
Ran 12 tests in 0.950s
```

The failure response is nice, clean, and exactly what you would expect from a Django Test Failure.

Unlike the `DjangoMercuryAPITestCase` class, the `DjangoPerformanceAPITestCase` offers a way to pinpoint specific performance problems at an extact spot.


## Wiki Update

As per issue https://github.com/ibrahim-sisar/EduLite/issues/139 , I will update with a new Wiki Page on Backend Testing Standards that showcases this new modular test structure and the new performance testing library.

### Django Mercury Best Practices

https://github.com/80-20-Human-In-The-Loop/Django-Mercury-Performance-Testing/wiki/API-Reference

Here are my ideas of how this library could be used within an project like EduLite, or any open source django app:

1. Use `DjangoMercuryAPITestCase` as an investigation/learning tool.
    - Transform an existing test case into this new class
    - Run to see performance stats on pre-set thresholds 
    - Look at tips/hints, try to fix problem, or increase thresholds
2. Ideally, switch to `DjangoPerformanceAPITestCase` once the performance issue is found
    - This class offers custom methods, and a `with` manager to assert performance metrics at specific spots of your cod
    - Much less terminal noise than the `DjangoMercury` counterpart.
    - Alerts you if too many queries, or if test takes too long or uses too much memory etc.
3. Each app has a tests/performance/ module
    - Performance-critical parts can be investigated and documented/tested through this tool
    - Once we fix a performance issue, the test suite ensures it stays fixed
    - If you want a test to be run manually (not by the full test suite), just skip putting  test_* in the filename

## Friend Request Acceptance Performance Fix

### The Investigation

So Mercury caught another performance issue - this time in the friend request acceptance endpoint. The test was failing with:

```sh
AssertionError: Accept involves multiple operations: Query count 14 is not less than 10
```

14 queries just to accept a friend request? That's wild! Time to investigate.

### The Problem

The `AcceptFriendRequestView` was fetching the friend request without any query optimization:

```python
# Before - users/views.py line 473
def post(self, request, request_pk, *args, **kwargs):
    friend_request = get_object_or_404(ProfileFriendRequest, pk=request_pk)
    # ... rest of the code
```

This led to classic N+1 query problems when:
1. Permission checks accessed `friend_request.receiver` 
2. The `accept()` method accessed `sender.user` and `receiver.user`
3. Each access triggered separate database queries

The `ProfileFriendRequest.accept()` method had the same issue:

```python
# Before - users/models.py line 321
req = type(self).objects.select_for_update().get(pk=self.pk)
req.receiver.friends.add(req.sender.user)  # More queries!
req.sender.friends.add(req.receiver.user)  # Even more queries!
```

### The Fix

Added `select_related` to prefetch all the relationships we need:

```python
# After - users/views.py
def post(self, request, request_pk, *args, **kwargs):
    # Optimize query with select_related to prevent N+1 queries
    friend_request = get_object_or_404(
        ProfileFriendRequest.objects.select_related(
            'sender__user', 
            'receiver__user'
        ), 
        pk=request_pk
    )
```

And in the model:

```python
# After - users/models.py
req = type(self).objects.select_for_update().select_related(
    'sender__user', 
    'receiver__user'
).get(pk=self.pk)
```

### The Results

**Before:** 14 queries 😱
**After:** 9 queries 🎉

That's a 36% reduction in database queries! The remaining 9 queries are actually reasonable:
- 1 for initial fetch with related data
- 1-2 for permission checks
- 1 for the select_for_update
- 2 for each M2M friend addition
- 1 for the delete

This optimization means friend request acceptance is now ~36% faster and puts less load on the database. The test suite will ensure this performance gain is maintained going forward.
