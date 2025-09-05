# users/views.py
import logging
import json
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiResponse,
    OpenApiParameter,
    OpenApiTypes,
    OpenApiExample,
)

from .models import (
    UserProfile,
    ProfileFriendRequest,
    UserProfilePrivacySettings,
    FriendSuggestion,
)

from .serializers import (
    UserSerializer,
    UserSearchSerializer,
    GroupSerializer,
    UserRegistrationSerializer,
    ProfileSerializer,
    ProfileFriendRequestSerializer,
    FriendSuggestionSerializer,
    UserProfilePrivacySettingsSerializer,
)

from .permissions import (
    IsProfileOwnerOrAdmin,
    IsUserOwnerOrAdmin,
    IsAdminUserOrReadOnly,
    IsFriendRequestReceiver,
    IsFriendRequestReceiverOrSender,
)
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
import json
import base64
logger = logging.getLogger(__name__)
performance_logger = logging.getLogger('performance')

class UsersAppBaseAPIView(APIView):
    """
    Enhanced base API view with automatic performance monitoring and alerting.
    Monitors response time and payload size, triggering alerts when thresholds exceeded.
    
    **Monitoring Thresholds:**
    - Response Time: 100ms (configurable via PERFORMANCE_MONITORING['RESPONSE_TIME_THRESHOLD'])
    - Payload Size: 10KB (configurable via PERFORMANCE_MONITORING['PAYLOAD_SIZE_THRESHOLD_KB'])
    
    **Configuration in settings.py:**
    PERFORMANCE_MONITORING = {
        'ENABLED': True,  # Enable monitoring
        'RESPONSE_TIME_THRESHOLD': 100,  # milliseconds
        'PAYLOAD_SIZE_THRESHOLD_KB': 10,  # kilobytes
        'LOG_ALL_REQUESTS': False,  # Only log threshold violations
        'LOG_LEVEL': 'WARNING',  # 'DEBUG', 'INFO', 'WARNING', 'ERROR'
    }
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        """
        Ensures that the request object is available to the serializer context.
        This is useful for HATEOAS link generation or other context-aware serialization.
        """
        return {"request": self.request}


# Rest of your views remain the same...
class UserListView(UsersAppBaseAPIView):
    """
    OPTIMIZED API view to list all users (with pagination).
    - GET: Returns a paginated list of users.
    Supports dynamic page_size via query parameter for performance testing.
    """
    
    # CLASS-LEVEL CONFIGURATION
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """
        Get the queryset with proper select_related to avoid N+1 queries.
        """
        return User.objects.select_related(
            'profile',  # For profile_url field and privacy checks
            'profile__privacy_settings',  # For privacy settings in serializer methods
            
        ).prefetch_related(
            'groups',  # If you're including group information
            
        ).order_by("-date_joined")
    
    def get(self, request, *args, **kwargs):
        """Handles LIST with minimal database queries."""
        # Get optimized queryset
        users = self.get_queryset()
        
        # Create paginator instance (not class-level)
        paginator = self.pagination_class()
        paginator.page_size = 10  # Default page size
        paginator.max_page_size = 100
        
        # Allow dynamic page_size for performance testing
        page_size = request.query_params.get('page_size')
        if page_size:
            try:
                page_size = int(page_size)
                # Respect max_page_size limit
                if page_size <= paginator.max_page_size:
                    paginator.page_size = page_size
            except (ValueError, TypeError):
                pass  # Invalid page_size, use default
        
        # Paginate the queryset
        page = paginator.paginate_queryset(users, request, view=self)
        
        if page is not None:
            # Use class, not instance
            serializer = self.serializer_class(
                page, many=True, context=self.get_serializer_context()
            )
            return paginator.get_paginated_response(serializer.data)
        
        # When pagination is not active, return full list
        serializer = self.serializer_class(
            users, many=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)


class UserRegistrationView(UsersAppBaseAPIView):
    """
    API view to register a new user.
    - POST: Creates a new user.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):  # Handles CREATE
        serializer = UserRegistrationSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        if serializer.is_valid():
            result = serializer.save()  # Returns either User or dict
            
            # Check if email verification is required
            from django.conf import settings
            require_verification = getattr(settings, 'USER_EMAIL_VERIFICATION_REQUIRED_FOR_SIGNUP', False)
            
            if require_verification:
                # Email verification required - return message only
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                # User created immediately - format response with user_id
                response_data = {
                    'message': 'User created successfully. Verification email sent.',
                    'user_id': result.id,
                    'username': result.username,
                    'email': result.email
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRetrieveView(UsersAppBaseAPIView):
    """
    API view to retrieve, update, or delete a specific user by their PK.
    - GET: Retrieves a user.
    """

    permission_classes = [permissions.IsAuthenticated]
    queryset_all = User.objects.select_related(
        'profile',
        'profile__privacy_settings'
    ).prefetch_related('groups')  # Optimized queryset for object lookup
    serializer_class_instance = UserSerializer

    def get_object(self, pk):
        """
        Helper method to retrieve the user object or raise a 404 error.
        """
        return get_object_or_404(self.queryset_all, pk=pk)

    def get(self, request, pk, *args, **kwargs):  # Handles RETRIEVE
        user = self.get_object(pk)
        serializer = self.serializer_class_instance(
            user, context=self.get_serializer_context()
        )
        return Response(serializer.data)


class UserUpdateDeleteView(UsersAppBaseAPIView):
    """
    API view to update or delete a specific user by their PK.
    Inherits from UsersAppBaseAPIView.
    - PUT: Updates a user.
    - PATCH: Partially updates a user.
    - DELETE: Deletes a user.
    """

    permission_classes = [IsUserOwnerOrAdmin]
    queryset_all = User.objects.select_related(
        'profile',
        'profile__privacy_settings'
    )
    serializer_class_instance = UserSerializer

    def get_object(self, pk):
        """
        Helper method to retrieve the user object or raise a 404 error.
        """
        obj = get_object_or_404(self.queryset_all, pk=pk)
        self.check_object_permissions(self.request, obj)
        return obj

    def put(self, request, pk, *args, **kwargs):  # Handles UPDATE
        user = self.get_object(pk)
        serializer = self.serializer_class_instance(
            user, data=request.data, context=self.get_serializer_context()
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):  # Handles PARTIAL_UPDATE
        user = self.get_object(pk)
        serializer = self.serializer_class_instance(
            user, data=request.data, partial=True, context=self.get_serializer_context()
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):  # Handles DESTROY
        user = self.get_object(pk)
        # Consider any pre-delete logic or checks here
        try:
            user.delete()
            return Response(
                {"message": "User deleted successfully."}, 
                status=status.HTTP_202_ACCEPTED
            )
        except Exception as e:
            logger.error(f"Failed to delete user {pk}: {str(e)}")
            return Response(
                {"message": "User could not be deleted!"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# --- Group API Views ---


class GroupListCreateView(UsersAppBaseAPIView):
    """
    API view to list all groups (with pagination) or create a new group.
    - GET: Returns a paginated list of groups.
    - POST: Creates a new group.
    """

    permission_classes = [IsAdminUserOrReadOnly]
    queryset_all = Group.objects.all().order_by("name")
    serializer_class_instance = GroupSerializer
    pagination_class_instance = PageNumberPagination
    pagination_class_instance.page_size = 10

    def get(self, request, *args, **kwargs):  # Handles LIST
        groups = self.queryset_all
        paginator = self.pagination_class_instance()
        page = paginator.paginate_queryset(groups, request, view=self)
        if page is not None:
            serializer = self.serializer_class_instance(
                page, many=True, context=self.get_serializer_context()
            )
            return paginator.get_paginated_response(serializer.data)
        # When pagination is not active or applicable, just return the full list
        serializer = self.serializer_class_instance(
            groups, many=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):  # Handles CREATE
        serializer = self.serializer_class_instance(
            data=request.data, context=self.get_serializer_context()
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupRetrieveUpdateDestroyView(UsersAppBaseAPIView):
    """
    API view to retrieve, update, or delete a specific group by its PK.
    Inherits from UsersAppBaseAPIView.
    - GET: Retrieves a group.
    - PUT: Updates a group.
    - PATCH: Partially updates a group.
    - DELETE: Deletes a group.
    """

    permission_classes = [IsAdminUserOrReadOnly]
    queryset_all = Group.objects.all()
    serializer_class_instance = GroupSerializer

    def get_object(self, pk):
        return get_object_or_404(self.queryset_all, pk=pk)

    def get(self, request, pk, *args, **kwargs):  # Handles RETRIEVE
        group = self.get_object(pk)
        serializer = self.serializer_class_instance(
            group, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):  # Handles UPDATE
        group = self.get_object(pk)
        serializer = self.serializer_class_instance(
            group, data=request.data, context=self.get_serializer_context()
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):  # Handles PARTIAL_UPDATE
        group = self.get_object(pk)
        serializer = self.serializer_class_instance(
            group,
            data=request.data,
            partial=True,
            context=self.get_serializer_context(),
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):  # Handles DESTROY
        group = self.get_object(pk)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -- User Profile API Views -- ##


class UserProfileRetrieveUpdateView(UsersAppBaseAPIView):
    """
    API view to retrieve, update, or delete a specific user profile by their PK.
    Inherits from UsersAppBaseAPIView.
    - GET: Retrieves a user profile.
    - PUT: Updates a user profile.
    - PATCH: Partially updates a user profile.
    """

    permission_classes = [permissions.IsAuthenticated, IsProfileOwnerOrAdmin]
    queryset_all = UserProfile.objects.all()  # Base queryset for object lookup
    serializer_class_instance = ProfileSerializer

    def get_object(self, pk):
        """
        Helper method to retrieve the UserProfile object by its pk.
        """
        obj = get_object_or_404(self.queryset_all, pk=pk)
        self.check_object_permissions(
            self.request, obj
        )  # DRF's way to check permissions on the object
        return obj

    def get(self, request, pk, *args, **kwargs):  # Handles RETRIEVE
        profile = self.get_object(pk)
        serializer = self.serializer_class_instance(
            profile, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):  # Handles UPDATE
        profile = self.get_object(pk)
        serializer = self.serializer_class_instance(
            profile, data=request.data, context=self.get_serializer_context()
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):  # Handles PARTIAL_UPDATE
        profile = self.get_object(pk)
        serializer = self.serializer_class_instance(
            profile,
            data=request.data,
            partial=True,
            context=self.get_serializer_context(),
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSearchView(UsersAppBaseAPIView):
    """
    API view to search for users by username, first name, or last name.
    Accepts a query parameter 'q'.
    - GET: Returns a paginated list of matching active users with privacy controls.
    
    Note: Anonymous users can search but will only see users with 'everyone' visibility.
    """

    permission_classes = [permissions.AllowAny]  # Allow anonymous users to search
    serializer_class_instance = UserSearchSerializer  # Use lightweight search serializer
    pagination_class_instance = PageNumberPagination

    def get(self, request, *args, **kwargs):
        from .logic.user_search_logic import execute_user_search

        search_query = request.query_params.get("q", "").strip()
        requesting_user = request.user if request.user.is_authenticated else None

        # Check if admin should bypass privacy filters
        bypass_privacy = requesting_user and requesting_user.is_superuser

        if not bypass_privacy:
            bypass_privacy = False

        # Get page_size from query params (default 10)
        page_size = request.query_params.get('page_size', '10')
        try:
            page_size = int(page_size)
            # Limit page size to prevent abuse
            page_size = min(max(page_size, 1), 100)
        except (ValueError, TypeError):
            page_size = 10
        
        # Execute the search with privacy controls using logic functions
        success, queryset, paginator, error_response = execute_user_search(
            search_query=search_query,
            requesting_user=requesting_user,
            request=request,
            view_instance=self,
            min_query_length=2,
            page_size=page_size,
            bypass_privacy_filters=bypass_privacy
        )

        # Return error response if validation failed
        if not success:
            return error_response

        # Handle paginated response
        if paginator is not None:
            # Get the page data that was set during pagination
            page_data = paginator.page
            serializer = self.serializer_class_instance(
                page_data, many=True, context=self.get_serializer_context()
            )
            return paginator.get_paginated_response(serializer.data)

        # Handle non-paginated response
        serializer = self.serializer_class_instance(
            queryset, many=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)


# -- Friend Suggestion API View -- ##


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="Authorization",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            required=True,
            description="Bearer token for authentication.",
        ),
    ],
)
class FriendSuggestionListView(UsersAppBaseAPIView):
    """API view to retrieve friend suggestions for the authenticated user.

    GET:
    - Returns a list of precomputed friend suggestions sorted by score.
    - Optional `type` query parameter filters suggestions by reason.
    """

    serializer_class = FriendSuggestionSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter suggestions by reason (case-insensitive)",
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="List of friend suggestions.",
                response=FriendSuggestionSerializer(many=True),
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
                response=inline_serializer(
                    name="UnauthorizedError",
                    fields={"detail": serializers.CharField()},
                ),
                examples=[
                    OpenApiExample(
                        "Unauthorized",
                        value={"detail": "Authentication credentials were not provided."},
                    )
                ],
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        """Retrieve friend suggestions for the authenticated user."""
        # Base queryset for current user's suggestions
        suggestions = FriendSuggestion.objects.filter(user=request.user)

        # Optional reason filter
        suggestion_type = request.query_params.get("type")
        if suggestion_type:
            suggestions = suggestions.filter(reason__iexact=suggestion_type)

        # Optimize related user/profile and order by relevance
        suggestions = suggestions.select_related(
            "suggested_user", "suggested_user__profile"
        ).order_by("-score")

        serializer = self.serializer_class(
            suggestions, many=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)


# -- Friend Request API Views -- ##


class AcceptFriendRequestView(UsersAppBaseAPIView):
    """
    API view to accept a friend request.
    - POST: Accepts a friend request.
    """

    permission_classes = [IsAuthenticated, IsFriendRequestReceiver]

    def post(self, request, request_pk, *args, **kwargs):
        # Optimize query with select_related to prevent N+1 queries
        friend_request = get_object_or_404(
            ProfileFriendRequest.objects.select_related(
                'sender__user', 
                'receiver__user'
            ), 
            pk=request_pk
        )

        # Manually trigger object-level permission check for APIView
        self.check_object_permissions(request, friend_request)

        if friend_request.accept():
            return Response(
                {"detail": "Friend request accepted."}, status=status.HTTP_200_OK
            )

        else:
            # This case might be hit if the request was deleted just before accept,
            # or if accept() method itself had an internal issue and returned False.
            return Response(
                {
                    "detail": "Failed to accept friend request. It might have been already processed or an error occurred."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class DeclineFriendRequestView(UsersAppBaseAPIView):
    """
    API view to decline or cancel a friend request.
    - POST: Declines/Cancels a specific friend request identified by request_pk.
    """

    permission_classes = [IsAuthenticated, IsFriendRequestReceiverOrSender]

    def post(self, request, request_pk, *args, **kwargs):
        friend_request = get_object_or_404(ProfileFriendRequest, pk=request_pk)

        self.check_object_permissions(request, friend_request)

        # Determine if the user was the sender (canceling) or receiver (declining)
        # for a more specific response message.
        action_taken_by_sender = friend_request.sender == request.user.profile

        if (
            friend_request.decline()
        ):  # Calls the model's decline method which deletes it
            if action_taken_by_sender:
                message = "Friend request canceled successfully."
            else:
                message = "Friend request declined successfully."
            return Response({"detail": message}, status=status.HTTP_200_OK)
        else:
            return Response(
                {
                    "detail": "Failed to process the friend request. It might have been already actioned or an unexpected error occurred."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class PendingFriendRequestListView(UsersAppBaseAPIView):
    """
    API view to list pending friend requests for the authenticated user.
    - GET: Returns a paginated list of received or sent friend requests.
    """

    serializer_class = ProfileFriendRequestSerializer  # Specify the serializer
    pagination_class = (
        PageNumberPagination  # Or your custom one, e.g., ChatRoomPagination if suitable
    )

    def get_queryset(self, request):
        user_profile = request.user.profile  # Assumes user.profile exists
        request_type = request.query_params.get("type", "received").lower()

        if request_type == "sent":
            # Get requests sent by the user
            queryset = user_profile.sent_friend_requests.all()
        elif request_type == "received":
            # Get requests received by the user
            queryset = user_profile.received_friend_requests.all()
        elif request_type == "all":
            # Get all pending requests (both sent and received)
            sent = user_profile.sent_friend_requests.all()
            received = user_profile.received_friend_requests.all()
            queryset = ProfileFriendRequest.objects.filter(
                Q(id__in=sent.values_list('id', flat=True)) |
                Q(id__in=received.values_list('id', flat=True))
            )
        else:
            # Default to received for backwards compatibility
            queryset = user_profile.received_friend_requests.all()

        # Pre-fetch related user details for sender/receiver to optimize
        # Also select_related on sender and receiver to avoid N+1 for profile IDs
        # Include privacy_settings to avoid N+1 queries for privacy checks
        queryset = queryset.select_related(
            "sender", 
            "receiver", 
            "sender__user", 
            "receiver__user",
            "sender__privacy_settings",
            "receiver__privacy_settings"
        )
        return queryset.order_by("-created_at")  # Ensure consistent ordering

    def get(self, request, *args, **kwargs):
        if not hasattr(request.user, "profile"):
            return Response(
                {"detail": "User profile not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset(request)

        paginator = self.pagination_class()

        page = paginator.paginate_queryset(queryset, request, view=self)

        if page is not None:
            # Pass context to serializer for HyperlinkedRelatedFields or SerializerMethodFields
            serializer = self.serializer_class(
                page, many=True, context=self.get_serializer_context()
            )
            return paginator.get_paginated_response(serializer.data)

        # Fallback if pagination is not applicable (e.g., queryset is empty and paginator returns None)
        serializer = self.serializer_class(
            queryset, many=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)


class SendFriendRequestView(UsersAppBaseAPIView):
    """
    API view to send a new friend request.
    - POST: Creates a new ProfileFriendRequest.
    """

    # permission_classes is inherited from UsersAppBaseAPIView ([IsAuthenticated])

    def post(self, request, *args, **kwargs):
        try:
            sender_profile = request.user.profile
        except UserProfile.DoesNotExist:
            return Response(
                {"detail": "Sender profile not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate input: receiver_profile_id
        receiver_profile_id = request.data.get("receiver_profile_id")
        if not receiver_profile_id:
            return Response(
                {"detail": "receiver_profile_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not isinstance(receiver_profile_id, int):
            return Response(
                {"detail": "Invalid receiver_profile_id. Must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        receiver_profile = get_object_or_404(UserProfile, pk=receiver_profile_id)

        # 1. Self-request check
        if sender_profile == receiver_profile:
            return Response(
                {"detail": "You cannot send a friend request to yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2. Already friends check (using the UserProfile.friends M2M to User)
        if sender_profile.friends.filter(pk=receiver_profile.user.pk).exists():
            return Response(
                {"detail": "You are already friends with this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3. Check for existing pending request (in either direction)
        # This also covers the UniqueConstraint on the model but gives a nicer API error.
        existing_request = ProfileFriendRequest.objects.filter(
            (Q(sender=sender_profile) & Q(receiver=receiver_profile))
            | (Q(sender=receiver_profile) & Q(receiver=sender_profile))
        ).first()

        if existing_request:
            if existing_request.sender == sender_profile:
                message = "You have already sent a friend request to this user."
            else:
                message = "This user has already sent you a friend request. Check your pending requests."
            return Response({"detail": message}, status=status.HTTP_400_BAD_REQUEST)
        
        # ✅ Get optional message
        message = request.data.get("message", "").strip()
        if len(message) > 500:
            return Response(
                {"detail": "Message must be 500 characters or fewer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # If all checks pass, create the friend request
        try:
            friend_request = ProfileFriendRequest.objects.create(
                sender=sender_profile, 
                receiver=receiver_profile, 
                message=message if message else None
            )
            return Response(
                {
                    "detail": "Friend request sent successfully.",
                    "request_id": friend_request.id
                },
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            # Handle different ValidationError formats
            if hasattr(e, "message_dict"):
                return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)
            elif hasattr(e, "messages"):
                return Response(
                    {"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:  # Catch IntegrityError from UniqueConstraint
            return Response(
                {
                    "detail": "A friend request between these users already exists or another integrity issue occurred."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


# -- Privacy Settings API Views -- ##


class UserProfilePrivacySettingsRetrieveUpdateView(UsersAppBaseAPIView):
    """
    API view to retrieve and update user privacy settings.
    - GET: Returns the current user's privacy settings.
    - PUT/PATCH: Updates the current user's privacy settings.
    """

    serializer_class_instance = UserProfilePrivacySettingsSerializer

    def get_object(self):
        """
        Get the privacy settings for the current user.
        Creates privacy settings if they don't exist (defensive programming).
        """
        user_profile = get_object_or_404(UserProfile, user=self.request.user)

        # Ensure privacy settings exist (defensive programming)
        privacy_settings, created = UserProfilePrivacySettings.objects.get_or_create(
            user_profile=user_profile
        )

        if created:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(
                "Created missing privacy settings for user %s",
                self.request.user.username
            )

        return privacy_settings

    def get(self, request, *args, **kwargs):
        """
        Retrieve the current user's privacy settings.
        """
        privacy_settings = self.get_object()
        serializer = self.serializer_class_instance(
            privacy_settings, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        """
        Update the current user's privacy settings (full update).
        """
        privacy_settings = self.get_object()
        serializer = self.serializer_class_instance(
            privacy_settings,
            data=request.data,
            context=self.get_serializer_context(),
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        """
        Partially update the current user's privacy settings.
        """
        privacy_settings = self.get_object()
        serializer = self.serializer_class_instance(
            privacy_settings,
            data=request.data,
            partial=True,
            context=self.get_serializer_context(),
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfilePrivacySettingsChoicesView(UsersAppBaseAPIView):
    """
    API view to get available privacy setting choices.
    - GET: Returns the available choices for privacy settings fields.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Return available choices for privacy settings.
        """
        from .models import SEARCH_VISIBILITY_CHOICES, PROFILE_VISIBILITY_CHOICES

        choices_data = {
            "search_visibility": [
                {"value": choice[0], "display_name": choice[1]}
                for choice in SEARCH_VISIBILITY_CHOICES
            ],
            "profile_visibility": [
                {"value": choice[0], "display_name": choice[1]}
                for choice in PROFILE_VISIBILITY_CHOICES
            ],
        }

        return Response(choices_data)



class EmailVerificationView(UsersAppBaseAPIView):
    """
    Handles email verification after registration.

    This view verifies the signed token received via the verification email link.
    If the token is valid and not expired, it decodes the user data and creates the user account.
    
    - Expects a 'token' in the query params.
    - The token is signed and base64-encoded JSON.
    - Token is valid for 1 hour (3600 seconds).
    - If the email is already registered, it returns an error.
    - On success, it creates the user and marks the account as active.
    """
    
    permission_classes = []

    def get(self, request):
        token = request.GET.get("token")
        if not token:
            return Response({"error": "Missing token"}, status=status.HTTP_400_BAD_REQUEST)

        signer = TimestampSigner()
        try:
            # Step 1: verify the signature
            unsigned = signer.unsign(token, max_age=3600)
            
            # Step 2: base64 decode the payload
            json_payload = base64.urlsafe_b64decode(unsigned.encode()).decode()

            # Step 3: load JSON
            data = json.loads(json_payload)

            if User.objects.filter(email=data["email"]).exists():
                return Response({"error": "User already exists."}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create_user(
                email=data["email"],
                username=data["username"],
                password=data["password"],
                first_name=data.get("first_name", ""),
                last_name=data.get("last_name", ""),
                is_active=True
            )
            return Response({"message": "Email verified and account created."})

        except (BadSignature, SignatureExpired):
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
