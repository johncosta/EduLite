# views.py
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination # For list views

from .models import UserProfile
from .serializers import (
    UserSerializer, GroupSerializer, UserRegistrationSerializer,
    ProfileSerializer
)
from .permissions import IsProfileOwnerOrAdmin, IsUserOwnerOrAdmin, IsAdminUserOrReadOnly

# --- Base API View for users App ---
class UsersAppBaseAPIView(APIView):
    """
    A custom base API view for the EduLite project.
    Provides default authentication permissions and a helper method to get serializer context.
    Other common functionalities for EduLite APIViews can be added here.
    
    **attribute** 'permission_classes' is set to [permissions.IsAuthenticated] by default.
    
    **method** 'get_serializer_context' is used to get the request object.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        """
        Ensures that the request object is available to the serializer context.
        This is useful for HATEOAS link generation or other context-aware serialization.
        """
        return {'request': self.request}


# --- User API Views ---


class UserListView(UsersAppBaseAPIView):
    """
    API view to list all users (with pagination).
    - GET: Returns a paginated list of users.
    """
    queryset_all = User.objects.all().order_by('-date_joined')
    serializer_class_instance = UserSerializer
    pagination_class_instance = PageNumberPagination
    pagination_class_instance.page_size = 10

    def get(self, request, *args, **kwargs): # Handles LIST
        users = self.queryset_all
        
        paginator = self.pagination_class_instance()
        page = paginator.paginate_queryset(users, request, view=self) 
        
        if page is not None:
            serializer = self.serializer_class_instance(page, many=True, context=self.get_serializer_context())
            return paginator.get_paginated_response(serializer.data)
            
        # When pagination is not active or applicable, just return the full list
        serializer = self.serializer_class_instance(users, many=True, context=self.get_serializer_context())
        return Response(serializer.data)


class UserRegistrationView(UsersAppBaseAPIView):
    """
    API view to register a new user.
    - POST: Creates a new user.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs): # Handles CREATE
        serializer = UserRegistrationSerializer(
            data=request.data, context=self.get_serializer_context()
            )
        if serializer.is_valid():
            user = serializer.save() # Calls create() in the serializer
            return Response(
                {'message': 'User created successfully.', 'user_id': user.id, 'username': user.username},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRetrieveView(UsersAppBaseAPIView):
    """
    API view to retrieve, update, or delete a specific user by their PK.
    - GET: Retrieves a user.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset_all = User.objects.all() # Base queryset for object lookup
    serializer_class_instance = UserSerializer

    def get_object(self, pk):
        """
        Helper method to retrieve the user object or raise a 404 error.
        """
        return get_object_or_404(self.queryset_all, pk=pk)

    def get(self, request, pk, *args, **kwargs): # Handles RETRIEVE
        user = self.get_object(pk)
        serializer = self.serializer_class_instance(
            user, 
            context=self.get_serializer_context()
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
    queryset_all = User.objects.all() # Base queryset for object lookup
    serializer_class_instance = UserSerializer
    
    def get_object(self, pk):
        """
        Helper method to retrieve the user object or raise a 404 error.
        """
        obj = get_object_or_404(self.queryset_all, pk=pk)
        self.check_object_permissions(self.request, obj)
        return obj
    
    def put(self, request, pk, *args, **kwargs): # Handles UPDATE
        user = self.get_object(pk)
        serializer = self.serializer_class_instance(
            user, 
            data=request.data, 
            context=self.get_serializer_context()
            )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs): # Handles PARTIAL_UPDATE
        user = self.get_object(pk)
        serializer = self.serializer_class_instance(
            user, 
            data=request.data, 
            partial=True, 
            context=self.get_serializer_context()
            )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs): # Handles DESTROY
        user = self.get_object(pk)
        # Consider any pre-delete logic or checks here
        user.delete()
        return Response({"message": "User deleted successfully."}, status=status.HTTP_202_ACCEPTED)


# --- Group API Views ---


class GroupListCreateView(UsersAppBaseAPIView):
    """
    API view to list all groups (with pagination) or create a new group.
    - GET: Returns a paginated list of groups.
    - POST: Creates a new group.
    """
    permission_classes = [IsAdminUserOrReadOnly]
    queryset_all = Group.objects.all().order_by('name')
    serializer_class_instance = GroupSerializer
    pagination_class_instance = PageNumberPagination
    pagination_class_instance.page_size = 10

    def get(self, request, *args, **kwargs): # Handles LIST
        groups = self.queryset_all
        paginator = self.pagination_class_instance()
        page = paginator.paginate_queryset(groups, request, view=self)
        if page is not None:
            serializer = self.serializer_class_instance(
                page, 
                many=True, 
                context=self.get_serializer_context()
                )
            return paginator.get_paginated_response(serializer.data)
        # When pagination is not active or applicable, just return the full list
        serializer = self.serializer_class_instance(
            groups, 
            many=True, 
            context=self.get_serializer_context()
            )
        return Response(serializer.data)

    def post(self, request, *args, **kwargs): # Handles CREATE
        serializer = self.serializer_class_instance(data=request.data, context=self.get_serializer_context())
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

    def get(self, request, pk, *args, **kwargs): # Handles RETRIEVE
        group = self.get_object(pk)
        serializer = self.serializer_class_instance(
            group, 
            context=self.get_serializer_context()
            )
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs): # Handles UPDATE
        group = self.get_object(pk)
        serializer = self.serializer_class_instance(
            group, 
            data=request.data, 
            context=self.get_serializer_context()
            )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs): # Handles PARTIAL_UPDATE
        group = self.get_object(pk)
        serializer = self.serializer_class_instance(
            group, 
            data=request.data, 
            partial=True, 
            context=self.get_serializer_context()
            )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs): # Handles DESTROY
        group = self.get_object(pk)
        group.delete()
        return Response({"message": "Group deleted successfully."}, status=status.HTTP_202_ACCEPTED)
    
    
## -- User Profile API Views -- ##


class UserProfileRetrieveUpdateView(UsersAppBaseAPIView):
    """
    API view to retrieve, update, or delete a specific user profile by their PK.
    Inherits from UsersAppBaseAPIView.
    - GET: Retrieves a user profile.
    - PUT: Updates a user profile.
    - PATCH: Partially updates a user profile.
    """
    permission_classes = [permissions.IsAuthenticated, IsProfileOwnerOrAdmin]
    queryset_all = UserProfile.objects.all() # Base queryset for object lookup
    serializer_class_instance = ProfileSerializer

    def get_object(self, pk):
        """
        Helper method to retrieve the UserProfile object by its pk.
        """
        obj = get_object_or_404(self.queryset_all, pk=pk)
        self.check_object_permissions(self.request, obj) # DRF's way to check permissions on the object
        return obj
    
    def get(self, request, pk, *args, **kwargs): # Handles RETRIEVE
        profile = self.get_object(pk)
        serializer = self.serializer_class_instance(
            profile, 
            context=self.get_serializer_context()
            )
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs): # Handles UPDATE
        profile = self.get_object(pk)
        serializer = self.serializer_class_instance(
            profile, 
            data=request.data, 
            context=self.get_serializer_context()
            )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs): # Handles PARTIAL_UPDATE
        profile = self.get_object(pk)
        serializer = self.serializer_class_instance(
            profile, 
            data=request.data, 
            partial=True, 
            context=self.get_serializer_context()
            )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)