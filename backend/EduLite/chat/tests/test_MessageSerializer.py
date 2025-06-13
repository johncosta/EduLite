from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.test import APIRequestFactory
from chat.serializers import MessageSerializer
from chat.models import ChatRoom, Message

User = get_user_model()


class MessageSerializerTest(TestCase):
    """Test case for Message Serializer"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="testuser1", email="user1@example.com", password="password123"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", email="user2@example.com", password="password123"
        )

        self.chat_room = ChatRoom.objects.create(
            name="Test chat", room_type="ONE_TO_ONE"
        )

        self.chat_room.participants.set([self.user1, self.user2])
        self.factory = APIRequestFactory()
        self.message = Message.objects.create(
            chat_room=self.chat_room, sender=self.user1, content="Hello, Anon!"
        )

    def test_create_message_uses_request_user_as_sender(self):
        """Test that the serializer uses request.user as sender if sender_id is not provided"""
        payload = {"content": "Hello, World!"}
        print(f"this is the payload': {payload}")
        request = self.factory.post("/api/messages", payload)
        request.user = self.user1

        serializer = MessageSerializer(data=payload, context={"request": request})

        self.assertTrue(serializer.is_valid(), serializer.errors)
        # Since chat_room is now read-only, we need to provide it at save time
        message = serializer.save(chat_room=self.chat_room)
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.content, "Hello, World!")
        self.assertEqual(message.chat_room, self.chat_room)
        print(message)

    def test_message_serializer_with_sender_id(self):
        """Test that the serializer uses sender_id if provided in the payload"""
        payload = {"sender_id": self.user2.id, "content": "Message from user2!"}
        serializer = MessageSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        # Since chat_room is now read-only, we need to provide it at save time
        message = serializer.save(chat_room=self.chat_room)
        self.assertEqual(message.sender, self.user2)
        self.assertEqual(message.content, "Message from user2!")
        self.assertEqual(message.chat_room, self.chat_room)

    def test_message_serializer_read_fields(self):
        """Test that the serializer returns the correct fields on read"""
        serializer = MessageSerializer(self.message)
        data = serializer.data
        self.assertIn("id", data)
        self.assertIn("chat_room", data)
        self.assertIn("sender", data)
        self.assertIn("content", data)
        self.assertIn("created_at", data)
        self.assertIn("is_read", data)
        self.assertEqual(data["sender"], str(self.user1))

    def test_message_serializer_invalid_sender(self):
        """Test that serializer is valid even if sender_id is not a participant

        Note: This test demonstrates that the serializer itself doesn't enforce
        participant validation - that should be handled at the view level.
        """
        # Create a user not in the chat room
        user3 = User.objects.create_user(
            username="user3", email="user3@example.com", password="password123"
        )
        payload = {"sender_id": user3.id, "content": "Should work at serializer level"}
        serializer = MessageSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        # Since chat_room is now read-only, we need to provide it at save time
        message = serializer.save(chat_room=self.chat_room)
        # The serializer does not enforce participant check, that's handled in views/permissions
        self.assertEqual(message.sender, user3)
        self.assertEqual(message.content, "Should work at serializer level")
        self.assertEqual(message.chat_room, self.chat_room)
