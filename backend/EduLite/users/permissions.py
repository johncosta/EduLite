# users/permissions.py

from rest_framework import permissions
from .models import UserProfile

class IsProfileOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of a UserProfile or admins to edit it.
    Read access (GET, HEAD, OPTIONS) is allowed for any authenticated user.
    """

    def has_permission(self, request, view) -> bool:
        # This initial check can ensure the user is authenticated before has_object_permission is called.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj: UserProfile) -> bool:
        """
        'obj' here is the UserProfile instance.
        """
        # Read permissions are allowed for any authenticated request if they passed has_permission.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed if the user is the owner of the profile
        # or if the user is an admin.
        return obj.user == request.user or request.user.is_staff


class IsUserOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission for the core User model.
    - Allows admins to perform any action.
    - Allows authenticated users to view (GET) any user's details (can be tightened if needed).
    - Allows a user to update (PUT, PATCH) or delete (DELETE) their own User record.
    """

    def has_permission(self, request, view):
        # Ensure the user is authenticated for any operation.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        'obj' here is the User instance (e.g., from get_user_model()).
        """
        # Admins (staff users) can do anything.
        if request.user.is_staff:
            return True

        # For non-admins:
        # If it's a safe method (GET, HEAD, OPTIONS), allow access.
        if request.method in permissions.SAFE_METHODS:
            return True

        # For unsafe methods (PUT, PATCH, DELETE), the user must be the object itself.
        return obj == request.user