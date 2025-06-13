from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from chat.pagination import ChatRoomPagination, MessageCursorPagination
from chat.models import ChatRoom, Message


class ChatRoomPaginationTest(APITestCase):
    """Test suite for ChatRoom pagination"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

        # Create 15 chat rooms (more than default page size of 10)
        self.chat_rooms = []
        for i in range(15):
            room = ChatRoom.objects.create(name=f"Test Room {i}", room_type="GROUP")
            room.participants.add(self.user)
            self.chat_rooms.append(room)

    def test_chatroom_pagination_page_size(self):
        """Test that pagination returns correct page size"""
        wsgi_request = self.factory.get("/api/chat/rooms/")
        wsgi_request.user = self.user
        request = Request(wsgi_request)  # Wrap with DRF Request
        paginator = ChatRoomPagination()
        queryset = ChatRoom.objects.all()

        result = paginator.paginate_queryset(queryset, request)
        response = paginator.get_paginated_response(result)

        self.assertEqual(len(result), paginator.page_size)  # Should be 10
        self.assertEqual(response.data["count"], 15)  # Total items
        self.assertEqual(
            response.data["total_pages"], 2
        )  # 15 items / 10 per page = 2 pages
        self.assertIsNotNone(response.data["next"])  # Should have next page
        self.assertIsNone(response.data["previous"])  # First page, no previous

    def test_chatroom_pagination_last_page(self):
        """Test pagination on the last page"""
        wsgi_request = self.factory.get("/api/chat/rooms/?page=2")
        wsgi_request.user = self.user
        request = Request(wsgi_request)  # Wrap with DRF Request
        paginator = ChatRoomPagination()
        queryset = ChatRoom.objects.all()

        result = paginator.paginate_queryset(queryset, request)
        response = paginator.get_paginated_response(result)

        self.assertEqual(len(result), 5)  # Last page should have 5 items
        self.assertIsNone(response.data["next"])  # Last page, no next
        self.assertIsNotNone(response.data["previous"])  # Should have previous page


class MessageCursorPaginationTest(APITestCase):
    """Test suite for Message cursor pagination"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.chat_room = ChatRoom.objects.create(name="Test Room", room_type="GROUP")
        self.chat_room.participants.add(self.user)

        # Create 60 messages (more than default page size of 50)
        self.messages = []
        for i in range(60):
            message = Message.objects.create(
                content=f"Test message {i}", chat_room=self.chat_room, sender=self.user
            )
            self.messages.append(message)

    def test_message_cursor_pagination_first_page(self):
        """Test first page of cursor pagination"""
        wsgi_request = self.factory.get("/api/chat/rooms/1/messages/")
        wsgi_request.user = self.user
        request = Request(wsgi_request)  # Wrap with DRF Request
        paginator = MessageCursorPagination()
        queryset = Message.objects.all()

        result = paginator.paginate_queryset(queryset, request)
        response = paginator.get_paginated_response(result)

        self.assertEqual(len(result), 50)  # Should be 50 items (default page size)
        self.assertIsNotNone(response.data["next"])  # Should have next page
        self.assertIsNone(response.data["previous"])  # First page, no previous

    def test_message_cursor_pagination_next_page(self):
        """Test cursor pagination when accessing next page"""
        # First, get the cursor from first page
        wsgi_request = self.factory.get("/api/chat/rooms/1/messages/")
        wsgi_request.user = self.user
        request = Request(wsgi_request)  # Wrap with DRF Request
        paginator = MessageCursorPagination()
        queryset = Message.objects.all()

        first_page = paginator.paginate_queryset(queryset, request)
        first_response = paginator.get_paginated_response(first_page)
        next_link = first_response.data["next"]

        # Now use the cursor to get next page
        cursor = next_link.split("cursor=")[1]
        wsgi_request = self.factory.get(f"/api/chat/rooms/1/messages/?cursor={cursor}")
        wsgi_request.user = self.user
        request = Request(wsgi_request)  # Wrap with DRF Request

        result = paginator.paginate_queryset(queryset, request)
        response = paginator.get_paginated_response(result)

        self.assertEqual(len(result), 10)  # Should be 10 items (remaining messages)
        self.assertIsNone(response.data["next"])  # Last page, no next
        self.assertIsNotNone(response.data["previous"])  # Should have previous page

    def test_message_ordering(self):
        """Test that messages are ordered by created_at timestamp"""
        wsgi_request = self.factory.get("/api/chat/rooms/1/messages/")
        wsgi_request.user = self.user

        print(wsgi_request.user)
        request = Request(wsgi_request)  # Wrap with DRF Request
        paginator = MessageCursorPagination()
        queryset = Message.objects.all()

        result = paginator.paginate_queryset(queryset, request)

        # Check that messages are ordered correctly (newest first)
        for i in range(len(result) - 1):
            self.assertGreaterEqual(result[i].created_at, result[i + 1].created_at)
