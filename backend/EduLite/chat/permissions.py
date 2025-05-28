from rest_framework import permissions

class IsParticipant(permissions.BasePermission):
    """
    Custom permission class to control ChatRoom access.
    
    Allows:
    - Room Creator: Full access to their created rooms
    - Participants: Read-only access to rooms they are part of
    - Others: No access
    """
    def has_permission(self, request, view):
        # Check if user is authenticated
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Allow read-only access for Chat Room participants
        if request.method in permissions.SAFE_METHODS:
            return obj.participants.filter(id=request.user.id).exists()
        
        # Write permissions are only allowed to the creator
        # Fixed typo in 'created_by'
        return hasattr(obj, 'created_by') and obj.created_by == request.user
    
class IsMessageSender(permissions.BasePermission):
    """
    Custom permission to allow only the sender of a message to delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Only allow delete if the user is the sender
        return request.user == obj.sender



