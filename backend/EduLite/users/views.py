from django.contrib.auth.models import User, Group
from rest_framework import generics, permissions
from .serializers import UserSerializer, GroupSerializer # Import your serializers

# --- User API Views ---

class UserListCreateView(generics.ListCreateAPIView):
    """
    API view to list all users or create a new user.
    Corresponds to GET (list) and POST (create) requests.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    # Since we don't have auth fully set up:
    permission_classes = [permissions.IsAuthenticated] # Or [permissions.AllowAny]


class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific user.
    Corresponds to GET (retrieve), PUT/PATCH (update), and DELETE requests.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    # Since we don't have auth fully set up:
    permission_classes = [permissions.IsAuthenticated] # Or [permissions.AllowAny]


# --- Group API Views ---

class GroupListCreateView(generics.ListCreateAPIView):
    """
    API view to list all groups or create a new group.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated] # Or [permissions.AllowAny]

class GroupRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific group.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated] # Or [permissions.AllowAny]
