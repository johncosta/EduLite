# views.py
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination # For list views

from .serializers import UserSerializer, GroupSerializer

# --- Base API View for EduLite ---
class EduLiteBaseAPIView(APIView):
    """
    A custom base API view for the EduLite project.
    Provides default authentication permissions and a helper method to get serializer context.
    Other common functionalities for EduLite APIViews can be added here.
    """
    permission_classes = [permissions.IsAuthenticated] # Default to requiring authentication

    def get_serializer_context(self):
        """
        Ensures that the request object is available to the serializer context.
        This is useful for HATEOAS link generation or other context-aware serialization.
        """
        return {'request': self.request}

    # You can add other common methods here


# --- User API Views ---

class UserListCreateView(EduLiteBaseAPIView):
    """
    API view to list all users (with pagination) or create a new user.
    Inherits from EduLiteBaseAPIView.
    - GET: Returns a paginated list of users.
    - POST: Creates a new user.
    """
    # Attributes used by our manual implementation
    queryset_all = User.objects.all().order_by('-date_joined')
    serializer_class_instance = UserSerializer
    pagination_class_instance = PageNumberPagination # Standard DRF pagination

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

    def post(self, request, *args, **kwargs): # Handles CREATE
        # For user creation, a more specialized way will be needed
        # for now, just use the basic UserSerializer 
        serializer = self.serializer_class_instance(data=request.data, context=self.get_serializer_context())
        if serializer.is_valid():
            # For user creation, a more specialized way will be needed
            # for now, just use the basic UserSerializer 
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRetrieveUpdateDestroyView(EduLiteBaseAPIView):
    """
    API view to retrieve, update, or delete a specific user by their PK.
    Inherits from EduLiteBaseAPIView.
    - GET: Retrieves a user.
    - PUT: Updates a user.
    - PATCH: Partially updates a user.
    - DELETE: Deletes a user.
    """
    queryset_all = User.objects.all() # Base queryset for object lookup
    serializer_class_instance = UserSerializer

    def get_object(self, pk):
        """
        Helper method to retrieve the user object or raise a 404 error.
        """
        return get_object_or_404(self.queryset_all, pk=pk)

    def get(self, request, pk, *args, **kwargs): # Handles RETRIEVE
        user = self.get_object(pk)
        serializer = self.serializer_class_instance(user, context=self.get_serializer_context())
        return Response(serializer.data)

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
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- Group API Views ---

class GroupListCreateView(EduLiteBaseAPIView):
    """
    API view to list all groups (with pagination) or create a new group.
    Inherits from EduLiteBaseAPIView.
    - GET: Returns a paginated list of groups.
    - POST: Creates a new group.
    """
    queryset_all = Group.objects.all().order_by('name')
    serializer_class_instance = GroupSerializer
    pagination_class_instance = PageNumberPagination

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


class GroupRetrieveUpdateDestroyView(EduLiteBaseAPIView):
    """
    API view to retrieve, update, or delete a specific group by its PK.
    Inherits from EduLiteBaseAPIView.
    - GET: Retrieves a group.
    - PUT: Updates a group.
    - PATCH: Partially updates a group.
    - DELETE: Deletes a group.
    """
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
        return Response(status=status.HTTP_204_NO_CONTENT)