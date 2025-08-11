# 🧪 Backend Testing Standards

> **Quality code starts with quality tests. Every test we write ensures EduLite works for students everywhere.**

## 🎯 Why Testing Matters

In a project serving students globally, testing ensures:
- **Reliability**: Features work in all conditions
- **Performance**: Code runs fast on slow networks
- **Maintainability**: Changes don't break existing features
- **Confidence**: Contributors can improve code safely
- **Documentation**: Tests show how code should work

**Our Goal**: Write tests that catch issues before students experience them.

---

## 📋 Table of Contents

- [Test Organization](#test-organization)
- [Test Types](#test-types)
- [Performance Testing](#performance-testing)
- [Writing Tests](#writing-tests)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Best Practices](#best-practices)
- [Mercury Framework](#mercury-framework)

---

## Test Organization

### Modular Test Structure

Our test suite is organized for efficiency and clarity:

```
users/tests/
├── __init__.py
├── fixtures/                    # Shared test data generators
│   ├── test_data_generators.py
│   └── bulk_test_users.py
├── logic/                      # Business logic tests
│   ├── test_user_search_logic.py
│   └── test_friend_request_logic.py
├── views/                      # API endpoint tests
│   ├── test_UserListView.py
│   ├── test_UserSearchView.py
│   └── test_SendFriendRequestView.py
├── models/                     # Model tests
│   ├── test_UserProfile.py
│   └── test_ProfileFriendRequest.py
├── serializers/                # Serializer tests
│   ├── test_UserSerializer.py
│   └── test_ProfileSerializer.py
├── management/                 # Management command tests
│   └── test_create_dummy_users.py
├── integration/                # End-to-end tests
│   └── test_registration_flow.py
└── performance/                # Performance tests
    ├── test_user_search_performance.py
    └── mercury_demo.py
```

### Running Specific Test Modules

```bash
# Test only logic functions
python manage.py test users.tests.logic

# Test only API views
python manage.py test users.tests.views

# Test only models
python manage.py test users.tests.models

# Test only serializers
python manage.py test users.tests.serializers

# Test management commands
python manage.py test users.tests.management

# Test integration flows
python manage.py test users.tests.integration

# Test performance
python manage.py test users.tests.performance

# Run all tests for an app
python manage.py test users

# Run with educational mode (Mercury)
python manage.py test --edu
```

---

## Test Types

### 1. Unit Tests (Logic & Models)

**Test individual functions and methods in isolation.**

```python
# users/tests/logic/test_user_search_logic.py

from django.test import TestCase
from ...logic.user_search_logic import validate_search_query

class ValidateSearchQueryTest(TestCase):
    """Test search query validation logic."""
    
    def test_valid_query(self):
        """Valid queries should return success."""
        success, query, error = validate_search_query("John", min_length=2)
        self.assertTrue(success)
        self.assertEqual(query, "john")  # Should be lowercased
        self.assertIsNone(error)
    
    def test_empty_query(self):
        """Empty queries should return error."""
        success, query, error = validate_search_query("", min_length=2)
        self.assertFalse(success)
        self.assertIsNotNone(error)
        self.assertIn("provide a search term", error.data["error"])
    
    def test_short_query(self):
        """Queries below min_length should fail."""
        success, query, error = validate_search_query("a", min_length=2)
        self.assertFalse(success)
        self.assertIn("at least 2 characters", error.data["error"])
```

### 2. API View Tests

**Test HTTP endpoints and responses.**

```python
# users/tests/views/test_UserSearchView.py

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

class UserSearchViewTest(TestCase):
    """Test user search API endpoint."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test data once for all tests."""
        # Create test users
        cls.john = User.objects.create_user(
            username='john_doe',
            first_name='John',
            last_name='Doe'
        )
        cls.jane = User.objects.create_user(
            username='jane_smith',
            first_name='Jane',
            last_name='Smith'
        )
    
    def setUp(self):
        """Set up test client for each test."""
        self.client = APIClient()
        self.client.force_authenticate(user=self.john)
    
    def test_search_by_username(self):
        """Should find users by username."""
        response = self.client.get('/api/users/search/?q=jane')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['username'], 'jane_smith')
    
    def test_search_requires_authentication(self):
        """Unauthenticated requests should be allowed but limited."""
        self.client.logout()
        response = self.client.get('/api/users/search/?q=john')
        
        # Anonymous users can search but see limited results
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_search_pagination(self):
        """Results should be paginated."""
        # Create many users
        for i in range(25):
            User.objects.create_user(username=f'user{i}')
        
        response = self.client.get('/api/users/search/?q=user')
        
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 10)  # Default page size
```

### 3. Serializer Tests

**Test data serialization and validation.**

```python
# users/tests/serializers/test_UserSerializer.py

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from ...serializers import UserSerializer

class UserSerializerTest(TestCase):
    """Test user serialization."""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
    
    def test_serializer_contains_expected_fields(self):
        """Serializer should include all expected fields."""
        request = self.factory.get('/')
        request.user = self.user
        
        serializer = UserSerializer(
            self.user, 
            context={'request': request}
        )
        
        data = serializer.data
        self.assertIn('id', data)
        self.assertIn('username', data)
        self.assertIn('email', data)
        self.assertIn('profile_url', data)
    
    def test_serializer_excludes_password(self):
        """Password should never be serialized."""
        serializer = UserSerializer(self.user)
        self.assertNotIn('password', serializer.data)
```

### 4. Integration Tests

**Test complete user flows across multiple components.**

```python
# users/tests/integration/test_registration_flow.py

from django.test import TransactionTestCase
from rest_framework.test import APIClient

class RegistrationFlowTest(TransactionTestCase):
    """Test complete user registration flow."""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_complete_registration_flow(self):
        """User should be able to register, login, and update profile."""
        
        # 1. Register new user
        registration_data = {
            'username': 'newstudent',
            'email': 'student@test.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }
        
        response = self.client.post(
            '/api/users/register/',
            data=registration_data,
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        user_id = response.data['user_id']
        
        # 2. Login with new credentials
        login_response = self.client.post(
            '/api/auth/login/',
            data={
                'username': 'newstudent',
                'password': 'SecurePass123!'
            }
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertIn('access', login_response.data)
        
        # 3. Update profile
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {login_response.data["access"]}'
        )
        
        profile_response = self.client.patch(
            f'/api/users/{user_id}/profile/',
            data={'bio': 'I love learning!'}
        )
        self.assertEqual(profile_response.status_code, 200)
        self.assertEqual(profile_response.data['bio'], 'I love learning!')
```

---

## Performance Testing

### Mercury Framework Overview

We use the **Django Mercury Performance Testing Framework** for identifying and preventing performance issues.

```bash
pip install django-mercury-performance==0.0.4
```

### Two Testing Approaches

#### 1. DjangoMercuryAPITestCase (Investigation Mode)

**Use for discovering performance issues:**

```python
from django_mercury import DjangoMercuryAPITestCase

class UserSearchPerformanceInvestigation(DjangoMercuryAPITestCase):
    """
    Investigate performance issues with automatic monitoring.
    Mercury will detect N+1 queries, slow operations, and memory issues.
    """
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Configure Mercury for investigation
        cls.configure_mercury(
            enabled=True,
            auto_scoring=True,              # Get performance grades
            verbose_reporting=True,         # See all issues
            educational_guidance=True,      # Get fix suggestions
        )
        
        # Set performance thresholds
        cls.set_performance_thresholds({
            'response_time_ms': 100,        # Flag if > 100ms
            'query_count_max': 10,          # Flag if > 10 queries
            'memory_overhead_mb': 30,       # Flag if > 30MB overhead
        })
    
    def test_search_with_many_results(self):
        """Test search performance with many users."""
        # Create 100 test users
        for i in range(100):
            User.objects.create_user(username=f'perf_user_{i}')
        
        # Mercury automatically monitors this request
        response = self.client.get('/api/users/search/?q=perf')
        
        # Mercury will report:
        # - Number of queries
        # - Response time
        # - Memory usage
        # - N+1 query detection
        # - Performance grade (A-F)
```

#### 2. DjangoPerformanceAPITestCase (Assertion Mode)

**Use for ongoing performance regression prevention:**

```python
from django_mercury import DjangoPerformanceAPITestCase
from django_mercury import monitor_django_view

class UserSearchPerformanceTest(DjangoPerformanceAPITestCase):
    """
    Assert specific performance requirements.
    Tests fail if performance degrades.
    """
    
    def test_search_performance_requirements(self):
        """Search must meet performance requirements."""
        # Create test data
        for i in range(50):
            User.objects.create_user(username=f'user_{i}')
        
        # Monitor specific operation
        with monitor_django_view("user_search") as monitor:
            response = self.client.get('/api/users/search/?q=user')
        
        # Assert performance requirements
        self.assertResponseTimeLess(monitor.metrics, 100, 
            "Search should complete within 100ms")
        
        self.assertQueriesLess(monitor.metrics, 5, 
            "Search should use 5 or fewer queries")
        
        self.assertMemoryLess(monitor.metrics, 150, 
            "Search should use less than 150MB memory")
        
        # Check for N+1 queries
        self.assertNoNPlusOneQueries(monitor.metrics,
            "Search should not have N+1 query problems")
```

### Best Practice: Investigation → Assertion

1. **Start with DjangoMercuryAPITestCase** to investigate
2. **Find and fix performance issues**
3. **Convert to DjangoPerformanceAPITestCase** to prevent regression

---

## Writing Tests

### Test Structure

```python
class TestClassName(TestCase):
    """
    Clear description of what's being tested.
    
    Explain any important context or assumptions.
    """
    
    @classmethod
    def setUpTestData(cls):
        """
        Create data once for all tests in class.
        Use this for read-only data.
        """
        cls.user = User.objects.create_user('testuser')
    
    def setUp(self):
        """
        Run before each test method.
        Use for test-specific setup.
        """
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_descriptive_name(self):
        """
        Test specific behavior or requirement.
        
        Follow pattern: test_what_when_expected
        """
        # Arrange - Set up test conditions
        data = {'key': 'value'}
        
        # Act - Perform the action
        result = function_under_test(data)
        
        # Assert - Check the outcome
        self.assertEqual(result, expected_value)
    
    def tearDown(self):
        """
        Clean up after each test.
        Usually not needed with transactions.
        """
        pass
```

### Naming Conventions

```python
# Test files: test_[WhatIsBeingTested].py
test_UserProfile.py
test_UserListView.py
test_friend_request_logic.py

# Test classes: [WhatIsBeingTested]Test
class UserProfileTest(TestCase):
class SendFriendRequestViewTest(TestCase):

# Test methods: test_[what]_[when]_[expected]
def test_profile_creation_with_valid_data_succeeds(self):
def test_search_with_empty_query_returns_error(self):
def test_friend_request_to_self_is_rejected(self):
```

### Fixtures and Test Data

#### Using Fixtures for Reusable Data

```python
# users/tests/fixtures/test_data_generators.py

def create_students_bulk(count=10):
    """Create multiple student users for testing."""
    students = []
    for i in range(count):
        user = User.objects.create_user(
            username=f'student_{i}',
            email=f'student{i}@test.com',
            first_name='Student',
            last_name=f'Number{i}'
        )
        students.append(user)
    return students

def setup_friend_relationships(users):
    """Create friend relationships between users."""
    for i, user in enumerate(users[:-1]):
        # Each user is friends with the next one
        user.profile.friends.add(users[i + 1])
```

#### Using Fixtures in Tests

```python
from ..fixtures.test_data_generators import create_students_bulk

class FriendshipTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.students = create_students_bulk(20)
        setup_friend_relationships(cls.students)
```

### Assertions

#### Common Assertions

```python
# Equality
self.assertEqual(actual, expected)
self.assertNotEqual(actual, expected)

# Truthiness
self.assertTrue(condition)
self.assertFalse(condition)

# Membership
self.assertIn(item, container)
self.assertNotIn(item, container)

# Exceptions
with self.assertRaises(ValidationError):
    invalid_operation()

# API responses
self.assertEqual(response.status_code, 200)
self.assertContains(response, "expected text")
self.assertJSONEqual(response.content, expected_json)

# Database
self.assertEqual(User.objects.count(), 5)
self.assertTrue(User.objects.filter(username='test').exists())
```

#### Custom Assertions (Mercury)

```python
# Performance assertions
self.assertResponseTimeLess(metrics, 100, "Should be fast")
self.assertQueriesLess(metrics, 10, "Should minimize queries")
self.assertMemoryLess(metrics, 50, "Should use minimal memory")
self.assertNoNPlusOneQueries(metrics, "Should avoid N+1")
```

---

## Running Tests

### Basic Commands

```bash
# Run all tests
python manage.py test

# Run with verbosity
python manage.py test --verbosity=2

# Run specific app tests
python manage.py test users

# Run specific test file
python manage.py test users.tests.views.test_UserListView

# Run specific test method
python manage.py test users.tests.views.test_UserListView.TestClass.test_method

# Keep test database between runs (faster)
python manage.py test --keepdb

# Run tests in parallel
python manage.py test --parallel

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Educational Mode (Mercury)

```bash
# Run with interactive educational feedback
python manage.py test --edu

# Mercury will:
# - Pause on failures
# - Explain what went wrong
# - Suggest fixes
# - Show performance metrics
# - Grade your code (A-F)
```

### Continuous Integration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python manage.py test --parallel
    
    - name: Run performance tests
      run: |
        python manage.py test users.tests.performance
```

---

## Test Coverage

### Target Coverage

```
Module          | Target | Minimum
----------------|--------|--------
Views           | 95%    | 80%
Models          | 90%    | 75%
Serializers     | 90%    | 75%
Business Logic  | 100%   | 90%
Utilities       | 100%   | 90%
```

### Measuring Coverage

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# Generate report
coverage report -m

# Generate HTML report
coverage html
# Open htmlcov/index.html in browser

# Check specific module
coverage report -m users/views.py
```

### Coverage Configuration

```ini
# .coveragerc
[run]
source = .
omit = 
    */migrations/*
    */tests/*
    */venv/*
    manage.py
    */settings/*
    */wsgi.py
    */asgi.py

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = htmlcov
```

---

## Best Practices

### 1. Test Isolation

```python
# ❌ BAD: Tests depend on each other
class BadTest(TestCase):
    def test_1_create_user(self):
        self.user = User.objects.create_user('test')
    
    def test_2_use_user(self):
        # This fails if test_1 doesn't run first!
        self.user.profile.bio = "Test"

# ✅ GOOD: Each test is independent
class GoodTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test')
    
    def test_update_bio(self):
        self.user.profile.bio = "Test"
        self.user.profile.save()
        self.assertEqual(self.user.profile.bio, "Test")
```

### 2. Use Appropriate Test Types

```python
# Use TestCase for database tests
class ModelTest(TestCase):
    """Tests that need database."""
    pass

# Use SimpleTestCase for non-database tests
class UtilityTest(SimpleTestCase):
    """Tests without database access."""
    pass

# Use TransactionTestCase for transaction tests
class TransactionTest(TransactionTestCase):
    """Tests that need real transactions."""
    pass
```

### 3. Test Data Patterns

```python
# ❌ BAD: Hardcoded test data everywhere
def test_something(self):
    user = User.objects.create_user(
        username='john',
        email='john@example.com',
        first_name='John',
        last_name='Doe'
    )

# ✅ GOOD: Reusable factories
from ..fixtures import create_test_user

def test_something(self):
    user = create_test_user(username='john')
```

### 4. Mock External Services

```python
from unittest.mock import patch, Mock

class EmailTest(TestCase):
    @patch('users.utils.send_email')
    def test_welcome_email_sent(self, mock_send):
        """Test that welcome email is sent on registration."""
        # Configure mock
        mock_send.return_value = True
        
        # Register user
        response = self.client.post('/api/register/', {...})
        
        # Verify email was "sent"
        mock_send.assert_called_once()
        self.assertIn('welcome', mock_send.call_args[0][0])
```

### 5. Test Error Cases

```python
def test_invalid_input_handling(self):
    """Always test error cases."""
    
    # Test with missing data
    response = self.client.post('/api/users/', {})
    self.assertEqual(response.status_code, 400)
    
    # Test with invalid data
    response = self.client.post('/api/users/', {
        'username': 'a',  # Too short
        'email': 'not-an-email'
    })
    self.assertEqual(response.status_code, 400)
    self.assertIn('username', response.data)
    self.assertIn('email', response.data)
```

### 6. Performance Test Patterns

```python
class PerformancePatterns(DjangoPerformanceAPITestCase):
    """Common performance testing patterns."""
    
    def test_pagination_performance(self):
        """Pagination should maintain performance with large datasets."""
        # Create large dataset
        users = [User(username=f'user_{i}') for i in range(1000)]
        User.objects.bulk_create(users)
        
        with monitor_django_view("paginated_list") as monitor:
            # First page should be fast regardless of total count
            response = self.client.get('/api/users/?page=1')
        
        self.assertResponseTimeLess(monitor.metrics, 100)
        self.assertQueriesLess(monitor.metrics, 5)
    
    def test_n_plus_one_prevention(self):
        """Check for N+1 query problems."""
        # Create related data
        for i in range(10):
            user = User.objects.create_user(f'user_{i}')
            user.profile.friends.add(*User.objects.all()[:5])
        
        with monitor_django_view("user_list_with_friends") as monitor:
            response = self.client.get('/api/users/')
        
        # Should use select_related/prefetch_related
        self.assertNoNPlusOneQueries(monitor.metrics)
```

---

## Mercury Framework

### Installation and Setup

```python
# settings.py
import sys

# Educational Test Runner via django-mercury-performance
if '--edu' in sys.argv:
    TEST_RUNNER = 'django_mercury.test_runner.EducationalTestRunner'
    sys.argv.remove('--edu')
```

### Mercury Dashboard

When using DjangoMercuryAPITestCase with verbose_reporting=True:

```
================================================================================
MERCURY PERFORMANCE REPORT - UserSearchView
================================================================================

📊 METRICS SUMMARY
├── Response Time: 45ms (✅ GOOD)
├── Database Queries: 122 (❌ EXCESSIVE)
├── Memory Usage: 12MB (✅ GOOD)
└── Performance Grade: D

⚠️  N+1 QUERY DETECTED
Location: UserSerializer.get_friends_count()
Problem: Accessing related model in loop
Solution: Use prefetch_related('friends') in queryset

📈 QUERY ANALYSIS
├── SELECT users: 1 query
├── SELECT profiles: 121 queries (N+1 ISSUE)
└── Total: 122 queries

💡 RECOMMENDATIONS
1. Add select_related('profile') to User queryset
2. Use prefetch_related('friends') for M2M relationships
3. Consider using only() to limit fields selected

================================================================================
```

### Writing Mercury Tests

```python
# users/tests/performance/mercury_demo.py

from django_mercury import DjangoMercuryAPITestCase

class MercuryDemoTest(DjangoMercuryAPITestCase):
    """
    Demonstration of Mercury capabilities.
    Run with: python manage.py test users.tests.performance.mercury_demo
    """
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Full Mercury configuration
        cls.configure_mercury(
            enabled=True,
            
            # Monitoring options
            monitor_requests=True,
            monitor_queries=True,
            monitor_cache=True,
            monitor_signals=True,
            
            # Reporting options
            auto_scoring=True,
            verbose_reporting=True,
            educational_guidance=True,
            
            # Analysis options
            detect_n_plus_one=True,
            suggest_indexes=True,
            analyze_similar_queries=True,
        )
        
        # Performance thresholds
        cls.set_performance_thresholds({
            'response_time_ms': 100,
            'query_count_max': 10,
            'similar_query_max': 3,
            'memory_overhead_mb': 30,
            'cache_hit_ratio_min': 0.8,
        })
    
    def test_comprehensive_analysis(self):
        """Mercury will analyze everything about this request."""
        response = self.client.get('/api/users/')
        
        # Mercury automatically:
        # - Counts queries
        # - Measures response time
        # - Tracks memory usage
        # - Detects N+1 queries
        # - Suggests optimizations
        # - Grades performance (A-F)
        # - Provides educational feedback
```

---

## Common Testing Patterns

### Testing Permissions

```python
class PermissionTest(TestCase):
    """Test that permissions are properly enforced."""
    
    def test_owner_can_edit_profile(self):
        """Profile owner should be able to edit."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            f'/api/profiles/{self.profile.id}/',
            {'bio': 'Updated bio'}
        )
        self.assertEqual(response.status_code, 200)
    
    def test_other_user_cannot_edit_profile(self):
        """Non-owner should not be able to edit."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(
            f'/api/profiles/{self.profile.id}/',
            {'bio': 'Hacked bio'}
        )
        self.assertEqual(response.status_code, 403)
    
    def test_unauthenticated_cannot_edit(self):
        """Unauthenticated user should not be able to edit."""
        self.client.logout()
        response = self.client.patch(
            f'/api/profiles/{self.profile.id}/',
            {'bio': 'Anonymous bio'}
        )
        self.assertEqual(response.status_code, 401)
```

### Testing Pagination

```python
class PaginationTest(TestCase):
    """Test API pagination."""
    
    @classmethod
    def setUpTestData(cls):
        # Create 25 users for pagination testing
        for i in range(25):
            User.objects.create_user(f'user_{i}')
    
    def test_default_page_size(self):
        """Should return 10 items by default."""
        response = self.client.get('/api/users/')
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(response.data['count'], 25)
    
    def test_custom_page_size(self):
        """Should respect page_size parameter."""
        response = self.client.get('/api/users/?page_size=5')
        self.assertEqual(len(response.data['results']), 5)
    
    def test_pagination_links(self):
        """Should provide next/previous links."""
        response = self.client.get('/api/users/?page=2')
        self.assertIsNotNone(response.data['next'])
        self.assertIsNotNone(response.data['previous'])
```

### Testing Filters

```python
class FilterTest(TestCase):
    """Test API filtering."""
    
    def test_filter_by_status(self):
        """Should filter users by status."""
        User.objects.create_user('active_user').profile.status = 'active'
        User.objects.create_user('inactive_user').profile.status = 'inactive'
        
        response = self.client.get('/api/users/?status=active')
        
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(
            response.data['results'][0]['username'], 
            'active_user'
        )
```

---

## Summary

Following these testing standards ensures:

1. **Reliability** - Code works correctly in all scenarios
2. **Performance** - Fast response times on slow networks
3. **Maintainability** - Safe refactoring with confidence
4. **Quality** - Bugs caught before production
5. **Documentation** - Tests show how code should work

### Remember

- **Test behavior, not implementation**
- **Each test should have one clear purpose**
- **Performance tests prevent regression**
- **Good tests are documentation**
- **Test the sad path, not just happy path**

---

*These standards evolve with our project. Suggest improvements via pull request!*

> 💚 **Every test you write is a promise to students that EduLite will work when they need it most. Test with purpose, test with care.**