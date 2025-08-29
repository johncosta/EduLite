# chat/consumers.py - WebSocket consumers for real-time chat functionality
# Handles WebSocket connections, authentication, and message broadcasting


"""
WebSocket consumers for EduLite chat functionality.

This module provides both production chat consumers and simple testing consumers
following Django's class-based view patterns and best practices.
"""

import json
import logging
from typing import Dict, Any, Optional
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from .models import ChatRoom, Message
from .serializers import MessageSerializer

User = get_user_model()
logger = logging.getLogger(__name__)




class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time chat functionality.

    Handles:
    - Room-based message broadcasting
    - Connection lifecycle management
    - Message persistence and delivery

    Authentication is handled by JWTAuthMiddleware prior to this consumer.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_id: Optional[str] = None
        self.room_group_name: Optional[str] = None
        self.user = None
        self.chat_room: Optional[ChatRoom] = None

    async def connect(self):
        """
        Handle WebSocket connection with middleware-authenticated user.

        Validates room access and adds the user to the room's channel group.
        Authentication is performed by the middleware before reaching this method.
        """
        try:
            # Extract authenticated user from middleware
            self.user = self.scope.get('user')

            if not self.user or isinstance(self.user, AnonymousUser):
                logger.warning(
                    "WebSocket connection rejected: unauthenticated user")
                await self.close(code=4001)  # Unauthorized
                return

            # Extract room ID from URL
            self.room_id = self.scope['url_route']['kwargs']['room_id']
            self.room_group_name = f'chat_{self.room_id}'

            # Validate room access
            self.chat_room = await self.get_chat_room()

            if not self.chat_room:
                logger.warning(
                    f"WebSocket connection rejected: room {self.room_id} not found")
                await self.close(code=4004)  # Not Found
                return

            if not await self.has_room_permission():
                logger.warning(
                    f"WebSocket connection rejected: user {self.user.id} lacks permission for room {self.room_id}")
                await self.close(code=4003)  # Forbidden
                return

            # Join room group for message broadcasting
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            # Accept the WebSocket connection
            await self.accept()

            logger.info(
                f"WebSocket connected: user {self.user.id} joined room {self.room_id}")

            # Notify other users about new connection
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_joined',
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'timestamp': timezone.now().isoformat()
                }
            )

        except Exception as e:
            logger.error(f"WebSocket connection error: {str(e)}")
            await self.close(code=4000)  # Generic server error

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection and cleanup.

        Removes user from the room group and notifies other participants.

        Args:
            close_code: WebSocket close code indicating reason for disconnection
        """
        if hasattr(self, 'room_group_name') and self.room_group_name and self.user:
            # Notify other users about disconnection
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'timestamp': timezone.now().isoformat()
                }
            )

            # Remove from room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

            logger.info(
                f"WebSocket disconnected: user {self.user.id} left room {self.room_id}, code: {close_code}")

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages from client.

        Parses the message and routes to appropriate handler based on message type.

        Expected message format:
        {
            "type": "chat_message",
            "message": "Hello, world!"
        }
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            # Route message to appropriate handler
            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'typing_indicator':
                await self.handle_typing_indicator(data)
            elif message_type == 'ping':
                await self.handle_ping()
            else:
                logger.warning(f"Unknown message type: {message_type}")
                await self.send_error("Unknown message type")

        except json.JSONDecodeError:
            logger.error("Invalid JSON received from WebSocket")
            await self.send_error("Invalid JSON format")
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {str(e)}")
            await self.send_error("Internal server error")

    async def handle_chat_message(self, data):
        """
        Handle chat message from client and broadcast to room.

        Saves message to database and broadcasts to all room participants.

        Args:
            data: Message data containing content
        """
        message_content = data.get('message', '').strip()

        if not message_content:
            await self.send_error("Message content cannot be empty")
            return

        if len(message_content) > 1000:  # Message length limit
            await self.send_error("Message too long")
            return

        try:
            # Save message to database using the same model as HTTP views
            message = await self.save_message(message_content)

            # Serialize message data
            message_data = await self.get_serialized_message(message)

            # Broadcast message to all users in the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message_broadcast',
                    'message': message_data
                }
            )

            logger.info(
                f"Message sent: user {self.user.id} in room {self.room_id}")

        except Exception as e:
            logger.error(f"Error handling chat message: {str(e)}")
            await self.send_error("Failed to send message")

    async def handle_typing_indicator(self, data):
        """
        Handle typing indicator and broadcast to other users in room.

        Args:
            data: Typing indicator data
        """
        is_typing = data.get('is_typing', False)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator_broadcast',
                'user_id': self.user.id,
                'username': self.user.username,
                'is_typing': is_typing,
                'timestamp': timezone.now().isoformat()
            }
        )

    async def handle_ping(self):
        """Handle ping message for connection health check."""
        await self.send(text_data=json.dumps({
            'type': 'pong',
            'timestamp': timezone.now().isoformat()
        }))

    # --- Message Broadcasting Handlers ---

    async def chat_message_broadcast(self, event):
        """
        Broadcast chat message to WebSocket client.

        Args:
            event: Event data containing message information
        """
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))

    async def typing_indicator_broadcast(self, event):
        """
        Broadcast typing indicator to WebSocket client.

        Args:
            event: Event data containing typing information
        """
        # Don't send typing indicator back to the sender
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing_indicator',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing'],
                'timestamp': event['timestamp']
            }))

    async def user_joined(self, event):
        """
        Broadcast user joined notification to WebSocket client.

        Args:
            event: Event data containing user information
        """
        # Don't send notification to the user who joined
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_joined',
                'user_id': event['user_id'],
                'username': event['username'],
                'timestamp': event['timestamp']
            }))

    async def user_left(self, event):
        """
        Broadcast user left notification to WebSocket client.

        Args:
            event: Event data containing user information
        """
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))

    # --- Database Operations ---

    @database_sync_to_async
    def get_chat_room(self):
        """
        Retrieve chat room from database.

        Returns:
            ChatRoom instance if found, None otherwise
        """
        try:
            return ChatRoom.objects.get(id=self.room_id)
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def has_room_permission(self):
        """
        Check if user has permission to access the chat room.

        Returns:
            True if user has permission, False otherwise
        """
        try:
            # Check if user is a participant in the room
            return self.chat_room.participants.filter(id=self.user.id).exists()
        except Exception:
            return False

    @database_sync_to_async
    def save_message(self, content):
        """
        Save message to database.

        Args:
            content: Message content

        Returns:
            Created Message instance
        """
        return Message.objects.create(
            chat_room=self.chat_room,
            sender=self.user,
            content=content
        )

    @database_sync_to_async
    def get_serialized_message(self, message):
        """
        Serialize message using existing MessageSerializer.

        Args:
            message: Message instance

        Returns:
            Serialized message data
        """
        # Using the same serializer as HTTP views for consistency
        return MessageSerializer(message).data

    # --- Utility Methods ---

    async def send_error(self, error_message):
        """
        Send error message to WebSocket client.

        Args:
            error_message: Error description
        """
        await self.send(text_data=json.dumps({
            'type': 'error',
            'error': error_message,
            'timestamp': timezone.now().isoformat()
        }))
