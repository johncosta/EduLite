# backend/EduLite/notifications/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from .models import Notification

User = get_user_model()


# -- Basic/Utility Serializers -- ##


class BasicUserSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for User model.
    Used for notifications and other contexts where minimal user info is needed.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
        ]
        read_only_fields = ["id", "username", "first_name", "last_name"]


# -- Notification Serializers -- ##


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model.
    Provides a comprehensive representation of notifications with actor and target details.
    """

    actor_details = BasicUserSerializer(source="actor", read_only=True)
    target_details = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Notification
        fields = [
            "id",
            "actor_details",
            "verb",
            "notification_type",
            "is_read",
            "created_at",
            "target_details",
        ]
        read_only_fields = [
            "id",
            "actor_details",
            "verb",
            "notification_type",
            "created_at",
            "target_details",
        ]

    def get_target_details(self, obj: Notification) -> dict[str, str | int | None]:
        """
        Returns details about the target object of the notification.
        Handles GenericForeignKey gracefully for any target model type.

        Returns:
            dict: Contains 'type', 'id', and 'display' keys with target information,
                  or None values if target doesn't exist.
        """
        if not obj.target:
            return {
                "type": None,
                "id": None,
                "display": None,
            }

        # Get the model name from the ContentType
        target_type = obj.target_content_type.model if obj.target_content_type else None

        return {
            "type": target_type,
            "id": obj.target_object_id,
            "display": str(obj.target),
        }
