"""
Chat application WebSocket routing configuration.

Defines URL patterns for real-time chat functionality including
room-based messaging and real-time communication features.
"""

from django.urls import re_path
from . import consumers

# Chat WebSocket URL patterns
websocket_urlpatterns = [
    # Chat room WebSocket connection
    # URL: ws://domain/ws/chat/<room_id>/
    re_path(
        r'ws/chat/(?P<room_id>\d+)/$',
        consumers.ChatConsumer.as_asgi(),
        name='chat_room_websocket'
    ),
    
    # Future chat-related WebSocket endpoints
    # Example: Private messaging, group chat notifications, etc.
]