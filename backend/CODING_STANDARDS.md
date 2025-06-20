# EduLite Backend Coding Standards

This document outlines the coding standards and best practices for the EduLite backend Django application. Following these standards ensures code consistency, maintainability, and readability across the project.

## Table of Contents

- [General Guidelines](#general-guidelines)
- [Views](#views)
- [Models](#models)
- [Serializers](#serializers)
- [Logic Extraction](#logic-extraction)
- [Testing](#testing)
- [Import Organization](#import-organization)
- [Documentation](#documentation)

---

## General Guidelines

### Code Organization and Separation

**Use whitespace and comment separators to organize code into logical groups:**

- **Single-line comments with dashes** (`# --- Section Name ---`) for major sections
- **Double-line comments with double dashes** (`# -- Subsection Name --`) for subsections within major sections
- **Consistent whitespace** (2-3 blank lines) between different groups of classes/functions
- **Single blank line** between methods within a class

**Example:**
```python
# --- User API Views ---


class UserListView(AppBaseAPIView):
    """List all users with pagination."""
    pass


class UserCreateView(AppBaseAPIView):
    """Create a new user."""
    pass


# -- User Profile Views --


class UserProfileView(AppBaseAPIView):
    """Handle user profile operations."""
    pass


# --- Group API Views ---


class GroupListView(AppBaseAPIView):
    """List all groups."""
    pass
```

### Type Annotations

**Always include type annotations** for function parameters and return types:

```python
from typing import Dict, List, Optional, Any
from django.http import HttpRequest
from rest_framework.response import Response

def process_user_data(user_id: int, data: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """Process user data and return result."""
    # Implementation here
    return {"status": "success"}

def get_user_list(request: HttpRequest) -> Response:
    """Get paginated list of users."""
    # Implementation here
    pass
```

### File Header Comments

**Every file should start with a comment indicating its purpose and location:**

```python
# users/views.py - User management API views for the EduLite platform
# Contains all user-related API endpoints including CRUD operations and friend requests

from django.contrib.auth.models import User
# ... other imports
```

---

## Views

### Base View Pattern

**Each Django app should have its own base API view** that inherits from `APIView` or appropriate DRF base classes. This promotes code reuse and consistent behavior across the app.

**Naming Convention:** `{AppName}AppBaseAPIView`

**Example:**
```python
# users/views.py
class UsersAppBaseAPIView(APIView):
    """
    Base API view for the users app in EduLite.
    Provides common functionality and default permissions for all user-related views.

    Default permissions: IsAuthenticated
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self) -> Dict[str, Any]:
        """
        Provides request context to serializers for HATEOAS and other context-aware operations.
        """
        return {"request": self.request}

    def handle_exception(self, exc: Exception) -> Response:
        """Custom exception handling for the users app."""
        # Custom exception logic here
        return super().handle_exception(exc)


# courses/views.py
class CoursesAppBaseAPIView(APIView):
    """
    Base API view for the courses app in EduLite.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self) -> Dict[str, Any]:
        return {"request": self.request}
```

### View Inheritance and Organization

**All views within an app should inherit from the app's base view:**

```python
# --- User CRUD Views ---


class UserListView(UsersAppBaseAPIView):
    """
    API view to list all users with pagination.
    - GET: Returns paginated list of users
    """

    def get(self, request: HttpRequest) -> Response:
        # Implementation
        pass


class UserCreateView(UsersAppBaseAPIView):
    """
    API view to create a new user.
    - POST: Creates a new user
    """

    def post(self, request: HttpRequest) -> Response:
        # Implementation
        pass


## -- User Profile Views -- ##


class UserProfileRetrieveUpdateView(UsersAppBaseAPIView):
    """
    API view to retrieve and update user profiles.
    - GET: Retrieve user profile
    - PUT/PATCH: Update user profile
    """

    def get_object(self) -> UserProfile:
        # Implementation
        pass

    def get(self, request: HttpRequest, pk: int) -> Response:
        # Implementation
        pass


# --- Friend Request Views ---


class SendFriendRequestView(UsersAppBaseAPIView):
    """
    API view to send friend requests.
    - POST: Send a friend request
    """

    def post(self, request: HttpRequest) -> Response:
        # Implementation
        pass
```

### View Documentation

**Every view class should have comprehensive docstrings:**

```python
class UserUpdateDeleteView(UsersAppBaseAPIView):
    """
    API view for updating and deleting user accounts.

    Endpoints:
    - PUT /users/{id}/: Update user (full update)
    - PATCH /users/{id}/: Partial update user
    - DELETE /users/{id}/: Delete user account

    Permissions:
    - IsUserOwnerOrAdmin: Only user themselves or admin can modify

    Returns:
    - 200: User updated successfully
    - 202: User deleted successfully
    - 403: Permission denied
    - 404: User not found
    """

    permission_classes = [IsUserOwnerOrAdmin]

    def get_object(self) -> User:
        """Retrieve user object with proper error handling."""
        # Implementation
        pass
```

---

## Logic Extraction

### When to Extract Logic

**Extract complex business logic into separate files when:**

- A method exceeds 20-30 lines of code
- Business logic is complex or contains multiple steps
- Logic could be reused across multiple views or apps
- The method contains complex database queries or data processing
- Testing would benefit from isolated logic units

### Logic File Structure

**Create a `logic/` directory within each app for extracted functions:**

```
users/
├── logic/
│   ├── __init__.py
│   ├── user_registration_logic.py
│   ├── friend_request_logic.py
│   ├── user_search_logic.py
│   └── profile_logic.py
├── views.py
├── models.py
└── ...
```

### Logic File Example

```python
# users/logic/friend_request_logic.py - Friend request business logic
# Contains all business logic related to friend request operations

from typing import Dict, List, Optional, Tuple
from django.contrib.auth.models import User
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import UserProfile, ProfileFriendRequest


def send_friend_request(sender: User, receiver_username: str) -> Tuple[bool, str]:
    """
    Send a friend request from sender to receiver.

    Args:
        sender: User sending the request
        receiver_username: Username of the user to send request to

    Returns:
        Tuple of (success: bool, message: str)

    Raises:
        ValidationError: If request is invalid
    """
    try:
        receiver = User.objects.get(username=receiver_username)

        # Validation logic
        if sender == receiver:
            return False, "Cannot send friend request to yourself"

        if are_already_friends(sender, receiver):
            return False, "Users are already friends"

        if has_pending_request(sender, receiver):
            return False, "Friend request already sent"

        # Create the friend request
        with transaction.atomic():
            ProfileFriendRequest.objects.create(
                from_user=sender.userprofile,
                to_user=receiver.userprofile,
                status='pending'
            )

        return True, "Friend request sent successfully"

    except User.DoesNotExist:
        return False, "User not found"
    except Exception as e:
        return False, f"Error sending friend request: {str(e)}"


def are_already_friends(user1: User, user2: User) -> bool:
    """Check if two users are already friends."""
    # Implementation here
    pass


def has_pending_request(sender: User, receiver: User) -> bool:
    """Check if there's already a pending friend request."""
    # Implementation here
    pass
```

### Using Extracted Logic in Views

```python
# users/views.py
from .logic.friend_request_logic import send_friend_request, accept_friend_request


class SendFriendRequestView(UsersAppBaseAPIView):
    """API view to send friend requests."""

    def post(self, request: HttpRequest) -> Response:
        """Send a friend request to another user."""
        receiver_username = request.data.get('receiver_username')

        if not receiver_username:
            return Response(
                {"error": "receiver_username is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use extracted logic
        success, message = send_friend_request(request.user, receiver_username)

        if success:
            return Response(
                {"message": message},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"error": message},
                status=status.HTTP_400_BAD_REQUEST
            )
```

---

## Models

### Model Organization

```python
# users/models.py - User-related models for the EduLite platform
# Contains User profiles, friend requests, and related functionality

from typing import Optional
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError

from .models_choices import OCCUPATION_CHOICES, COUNTRY_CHOICES, LANGUAGE_CHOICES


class UserProfile(models.Model):
    """Extended user profile with additional fields for EduLite platform."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    bio = models.TextField(max_length=500, blank=True, help_text="User biography")
    occupation = models.CharField(
        max_length=64, choices=OCCUPATION_CHOICES, blank=True, null=True
    )
    country = models.CharField(
        max_length=64, choices=COUNTRY_CHOICES, blank=True, null=True
    )
    preferred_language = models.CharField(
        max_length=64, choices=LANGUAGE_CHOICES, blank=True, null=True
    )
    secondary_language = models.CharField(
        max_length=64, choices=LANGUAGE_CHOICES, blank=True, null=True
    )

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def clean(self) -> None:
        """Custom validation for the model."""
        super().clean()
        if self.preferred_language and self.secondary_language:
            if self.preferred_language == self.secondary_language:
                raise ValidationError({
                    'secondary_language': "Secondary language cannot be the same as preferred language."
                })

    def __str__(self) -> str:
        return f"{self.user.username}'s Profile"

    def get_full_name(self) -> str:
        """Return user's full name or username if not available."""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username
```

### Dynamic Choices System

**EduLite uses a centralized system for managing model choices through JSON files. This allows contributors to easily add new countries, languages, professions, etc., without modifying Python code.**

#### Structure Overview

```
backend/
├── project_choices_data/           # JSON files for model choices
│   ├── countries.json             # Country options
│   ├── languages.json             # Language options
│   └── occupations.json           # Profession/occupation options
└── EduLite/
    └── users/
        ├── models_choices.py      # Python interface to JSON data
        └── models.py             # Models using the choices
```

#### models_choices.py - The Interface

```python
# users/models_choices.py - Dynamic choices loader for EduLite models
# Loads choices from JSON files to make them easily maintainable

import json
from pathlib import Path
from django.conf import settings
from typing import List, Tuple


CHOICES_DATA_DIR = Path(settings.BASE_DIR).parent / "project_choices_data"


def load_choices_from_json(filename: str) -> List[Tuple[str, str]]:
    """
    Load choices from JSON file and return as Django choices format.

    Args:
        filename: Name of the JSON file in project_choices_data directory

    Returns:
        List of (value, label) tuples for use in model CharField choices

    JSON Format Expected:
        [
            {"value": "code", "label": "Display Name"},
            {"value": "US", "label": "United States"},
            ...
        ]
    """
    file_path = CHOICES_DATA_DIR / filename
    choices_list = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                if isinstance(item, dict) and "value" in item and "label" in item:
                    choices_list.append((item["value"], item["label"]))
                else:
                    print(f"Warning: Malformed item in {filename}: {item}")

    except FileNotFoundError:
        print(f"Warning: Choices file not found: {file_path}")
    except json.JSONDecodeError:
        print(f"Warning: Invalid JSON in {file_path}")
    except Exception as e:
        print(f"Warning: Error loading {filename}: {e}")

    return choices_list


# Load all choices (loaded once when Django starts)
OCCUPATION_CHOICES = load_choices_from_json("occupations.json")
COUNTRY_CHOICES = load_choices_from_json("countries.json")
LANGUAGE_CHOICES = load_choices_from_json("languages.json")
```

#### JSON File Format

**Each JSON file follows a consistent structure:**

```json
// project_choices_data/countries.json
[
    {"value": "AF", "label": "Afghanistan"},
    {"value": "PL", "label": "Palestine"},
    {"value": "EG", "label": "Egypt"},
    {"value": "SD", "label": "Sudan"},
    {"value": "US", "label": "United States"},
    {"value": "CA", "label": "Canada"}
]
```

```json
// project_choices_data/occupations.json
[
    {"value": "teacher", "label": "Teacher"},
    {"value": "professor", "label": "Professor"},
    {"value": "student", "label": "Student"},
    {"value": "frontend_developer", "label": "Frontend Developer"},
    {"value": "backend_developer", "label": "Backend Developer"}
]
```

```json
// project_choices_data/languages.json
[
    {"value": "en", "label": "English"},
    {"value": "ar", "label": "Arabic"},
    {"value": "es", "label": "Spanish"},
    {"value": "fr", "label": "French"}
]
```

#### Benefits of This System

1. **Easy Contributions**: Contributors can add new options by editing JSON files
2. **No Code Changes**: Adding countries/languages doesn't require Python knowledge
3. **Centralized Management**: All choices are managed in one location
4. **Internationalization Ready**: Labels can be easily translated
5. **Version Control Friendly**: JSON changes are easy to review in pull requests
6. **Runtime Loading**: Choices are loaded once at startup for performance

#### Adding New Choices

**To add new options, contributors simply:**

1. **Edit the appropriate JSON file**:
   ```json
   // Add to project_choices_data/countries.json
   {"value": "JP", "label": "Japan"}
   ```

2. **Follow the format**: Each entry must have `"value"` and `"label"` keys

3. **Submit a pull request**: Changes are reviewed and merged

**No Python code modifications needed!**

#### Usage in Models

**The choices are imported and used directly in model fields:**

```python
from .models_choices import OCCUPATION_CHOICES, COUNTRY_CHOICES, LANGUAGE_CHOICES

class UserProfile(models.Model):
    occupation = models.CharField(
        max_length=64,
        choices=OCCUPATION_CHOICES,
        blank=True,
        null=True,
        help_text="Select your profession"
    )
    country = models.CharField(
        max_length=64,
        choices=COUNTRY_CHOICES,
        blank=True,
        null=True,
        help_text="Select your country"
    )
```

This system makes EduLite highly maintainable and contributor-friendly, allowing the community to easily expand the platform's options without technical barriers.

---

## Serializers

### Serializer Organization and Development vs Production

**Organize serializers by section using comment separators:**

```python
# users/serializers.py - Serializers for user-related models
# Contains serializers for User, UserProfile, and friend request models

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.urls import reverse
from rest_framework import serializers
from .models import UserProfile, ProfileFriendRequest


# -- User/Group Hyperlinked Serializers --


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for User model with hyperlinked relationships.

    Note: Hyperlinks are only included in development mode (DEBUG=True).
    In production, these will be stripped out for performance and security.
    """

    profile_url = serializers.HyperlinkedRelatedField(
        source="userprofile",
        view_name="userprofile-detail",
        read_only=True,
    )
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "url",  # URL for the User instance itself
            "profile_url",  # URL for the UserProfile instance
            "username",
            "email",
            "groups",
            "first_name",
            "last_name",
            "full_name",
        ]

    def get_full_name(self, obj: User) -> str:
        """Get user's full name."""
        first = obj.first_name
        last = obj.last_name
        if first and last:
            return f"{first} {last}"
        elif first:
            return first
        elif last:
            return last
        return ""

    def to_representation(self, instance):
        """
        Override to remove hyperlinked fields in production.
        In production (DEBUG=False), we strip out URL fields for performance.
        """
        data = super().to_representation(instance)

        if not settings.DEBUG:
            # Remove hyperlinked fields in production
            data.pop('url', None)
            data.pop('profile_url', None)

        return data


# -- Profile Serializers --


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for UserProfile model with hyperlinked relationships.

    Includes development-only hyperlinks that are removed in production.
    """

    user_url = serializers.HyperlinkedRelatedField(
        source="user",
        view_name="user-detail",
        read_only=True,
    )

    class Meta:
        model = UserProfile
        fields = [
            "url",  # URL for the UserProfile instance itself
            "user_url",  # URL for the related User instance
            "bio",
            "occupation",
            "country",
            "preferred_language",
            "secondary_language",
            "picture",
            "website_url",
            "friends",
        ]

    def to_representation(self, instance):
        """Remove hyperlinked fields in production."""
        data = super().to_representation(instance)

        if not settings.DEBUG:
            data.pop('url', None)
            data.pop('user_url', None)

        return data


# -- Friend Request Serializers --


class ProfileFriendRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for ProfileFriendRequest model.

    Uses SerializerMethodField to generate action URLs dynamically.
    These URLs are only included in development mode.
    """

    # Development-only action URLs
    sender_profile_url = serializers.SerializerMethodField()
    receiver_profile_url = serializers.SerializerMethodField()
    accept_url = serializers.SerializerMethodField()
    decline_url = serializers.SerializerMethodField()

    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = ProfileFriendRequest
        fields = [
            "id",
            "sender_id",
            "receiver_id",
            "sender_profile_url",
            "receiver_profile_url",
            "created_at",
            "accept_url",
            "decline_url",
        ]
        read_only_fields = ["id", "created_at"]

    def get_sender_profile_url(self, obj: ProfileFriendRequest) -> str | None:
        """Generate sender profile URL - development only."""
        if not settings.DEBUG:
            return None

        request = self.context.get("request")
        if request and obj.sender:
            return request.build_absolute_uri(
                reverse("userprofile-detail", kwargs={"pk": obj.sender.pk})
            )
        return None

    def get_receiver_profile_url(self, obj: ProfileFriendRequest) -> str | None:
        """Generate receiver profile URL - development only."""
        if not settings.DEBUG:
            return None

        request = self.context.get("request")
        if request and obj.receiver:
            return request.build_absolute_uri(
                reverse("userprofile-detail", kwargs={"pk": obj.receiver.pk})
            )
        return None

    def get_accept_url(self, obj: ProfileFriendRequest) -> str | None:
        """Generate accept action URL - development only."""
        if not settings.DEBUG:
            return None

        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(
                reverse("friend-request-accept", kwargs={"request_pk": obj.pk})
            )
        return None

    def get_decline_url(self, obj: ProfileFriendRequest) -> str | None:
        """Generate decline action URL - development only."""
        if not settings.DEBUG:
            return None

        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(
                reverse("friend-request-decline", kwargs={"request_pk": obj.pk})
            )
        return None

    def to_representation(self, instance):
        """Remove URL fields entirely in production."""
        data = super().to_representation(instance)

        if not settings.DEBUG:
            # Remove all URL fields in production
            url_fields = ['sender_profile_url', 'receiver_profile_url', 'accept_url', 'decline_url']
            for field in url_fields:
                data.pop(field, None)

        return data
```

### Hyperlinked Serializer Best Practices

**Use hyperlinked serializers for development convenience, but strip them in production:**

1. **Development Mode** (`DEBUG=True`):
   - Include hyperlinked fields for easy API exploration
   - Provide action URLs for frontend convenience
   - Enable HATEOAS (Hypermedia as the Engine of Application State)

2. **Production Mode** (`DEBUG=False`):
   - Remove hyperlinked fields for performance
   - Reduce response payload size
   - Eliminate potential security concerns with exposed URLs

3. **Implementation Pattern**:
   - Use `HyperlinkedModelSerializer` for main resource serializers
   - Use `SerializerMethodField` for dynamic URL generation
   - Override `to_representation()` to conditionally remove URL fields
   - Check `settings.DEBUG` to determine inclusion of hyperlinked fields

**Example of conditional URL field inclusion:**

```python
def to_representation(self, instance):
    """Conditionally include hyperlinked fields based on DEBUG setting."""
    data = super().to_representation(instance)

    if not settings.DEBUG:
        # Remove hyperlinked fields in production
        hyperlink_fields = ['url', 'profile_url', 'action_url']
        for field in hyperlink_fields:
            data.pop(field, None)

    return data
```

---

## Testing

### Test File Organization and Structure

**Organize tests using a modular directory structure within each app's `tests/` directory:**

```
users/
├── tests/
│   ├── __init__.py
│   ├── test_UserListView.py              # Individual view tests
│   ├── test_UserRegistrationView.py      # One file per view class
│   ├── test_SendFriendRequestView.py
│   ├── test_UserProfile.py               # Model tests
│   ├── test_ProfileFriendRequest.py
│   ├── functions/                        # Function-specific tests
│   │   ├── __init__.py
│   │   ├── test_generate_dummy_users_data.py
│   │   ├── test_create_notification_on_friend_request.py
│   │   └── test_establish_random_friendships.py
│   ├── serializers/                      # Serializer tests
│   │   ├── __init__.py
│   │   ├── test_UserSerializer.py
│   │   └── test_ProfileFriendRequestSerializer.py
│   ├── views/                           # Optional: Group view tests
│   │   ├── __init__.py
│   │   ├── test_user_crud_views.py
│   │   └── test_friend_request_views.py
│   └── models/                          # Optional: Group model tests
│       ├── __init__.py
│       └── test_user_models.py
├── views.py
├── models.py
└── ...
```

### Test File Naming Conventions

**Follow consistent naming patterns:**

- **View Tests**: `test_{ClassName}.py` (e.g., `test_UserListView.py`)
- **Model Tests**: `test_{ModelName}.py` (e.g., `test_UserProfile.py`)
- **Function Tests**: `functions/test_{function_name}.py`
- **Serializer Tests**: `serializers/test_{SerializerName}.py`
- **Permission Tests**: `test_{permission_name}.py`

### Test Organization Benefits

**This modular structure provides:**

- **Easy Navigation**: Quickly find tests for specific components
- **Better Test Isolation**: Each test file focuses on one component
- **Scalable Structure**: Add new test categories (e.g., `middleware/`, `utils/`) as needed
- **Clear Responsibility**: Each directory has a specific testing purpose
- **Team Collaboration**: Multiple developers can work on different test areas without conflicts

### Example Test File Structure

```python
# users/tests/test_UserListView.py - Tests for UserListView API endpoint
# Contains comprehensive tests for user list retrieval functionality

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch


class UserListViewTest(TestCase):
    """Test cases for UserListView API endpoint."""

    def setUp(self) -> None:
        """Set up test data for each test method."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_get_user_list_success(self) -> None:
        """Test successful retrieval of user list with pagination."""
        response = self.client.get('/api/users/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)

    def test_get_user_list_unauthorized(self) -> None:
        """Test that unauthorized users cannot access user list."""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/users/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('users.views.logger')
    def test_get_user_list_logs_access(self, mock_logger) -> None:
        """Test that user list access is properly logged."""
        self.client.get('/api/users/')

        mock_logger.info.assert_called_once()
```

### Testing Subdirectories

**Create subdirectories for specific test categories:**

```python
# users/tests/functions/test_generate_dummy_users_data.py
# Tests for the generate_dummy_users_data utility function

from django.test import TestCase
from unittest.mock import patch
from ..functions.dummy_data import generate_dummy_users_data


class GenerateDummyUsersDataTest(TestCase):
    """Test cases for generate_dummy_users_data function."""

    def test_generates_correct_number_of_users(self) -> None:
        """Test that function generates the requested number of users."""
        count = 5
        users = generate_dummy_users_data(count)

        self.assertEqual(len(users), count)
```

---

## Import Organization

### Import Order and Grouping

```python
# Standard library imports
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime

# Django imports
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

# Django REST framework imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

# Local app imports
from .models import UserProfile, ProfileFriendRequest
from .serializers import UserSerializer, GroupSerializer
from .permissions import IsProfileOwnerOrAdmin
from .logic.friend_request_logic import send_friend_request
```

---

## Documentation

### Docstring Standards

**Use Google-style docstrings for all functions and classes:**

```python
def process_friend_request(request_id: int, action: str) -> Dict[str, Any]:
    """
    Process a friend request with the specified action.

    Args:
        request_id: ID of the friend request to process
        action: Action to take ('accept' or 'decline')

    Returns:
        Dictionary containing success status and message

    Raises:
        ValidationError: If action is invalid
        ObjectDoesNotExist: If friend request not found

    Example:
        >>> result = process_friend_request(123, 'accept')
        >>> print(result['message'])
        'Friend request accepted successfully'
    """
    # Implementation here
    pass
```

---

## Error Handling

### Consistent Error Responses

```python
class UsersAppBaseAPIView(APIView):
    """Base view with standardized error handling."""

    def handle_validation_error(self, error: ValidationError) -> Response:
        """Handle validation errors consistently."""
        return Response(
            {"error": "Validation failed", "details": error.message_dict},
            status=status.HTTP_400_BAD_REQUEST
        )

    def handle_not_found(self, model_name: str) -> Response:
        """Handle not found errors consistently."""
        return Response(
            {"error": f"{model_name} not found"},
            status=status.HTTP_404_NOT_FOUND
        )
```

---

## Summary

Following these coding standards ensures:

- **Consistency** across the EduLite backend codebase
- **Maintainability** through clear organization and documentation
- **Testability** through modular test structure and proper logic separation
- **Readability** through consistent formatting and naming
- **Scalability** through modular architecture
- **Performance** through conditional hyperlink inclusion based on environment

Remember: If a method becomes too complex, extract it into the `logic/` directory. Keep views focused on HTTP request/response handling, and move business logic to dedicated logic modules.
