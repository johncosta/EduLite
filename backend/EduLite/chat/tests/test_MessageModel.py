from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from chat.models import ChatRoom, Message
from django.utils import timezone


class MessageModelTest(TestCase):
    """Test cases for the Message model."""

    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username="testuser1", email="user1@example.com", password="password123"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", email="user2@example.com", password="password123"
        )
        self.chat_room = ChatRoom.objects.create(
            name="Test Chat Room", room_type="ONE_TO_ONE"
        )
        self.chat_room.participants.add(self.user1, self.user2)

    def test_create_message(self):
        """Test creating a basic message"""
        message = Message.objects.create(
            chat_room=self.chat_room,
            sender=self.user1,
            content="Hello, this is a test message!",
        )

        self.assertEqual(message.content, "Hello, this is a test message!")
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.chat_room, self.chat_room)
        self.assertFalse(message.is_read)

    def test_message_timestamps(self):
        """Test that message timestamps are set correctly"""
        message = Message.objects.create(
            chat_room=self.chat_room, sender=self.user1, content="Test message"
        )

        self.assertIsNotNone(message.created_at)
        self.assertLessEqual(message.created_at, timezone.now())

    def test_message_ordering(self):
        """Test that messages are ordered by created_at"""
        message1 = Message.objects.create(
            chat_room=self.chat_room, sender=self.user1, content="First message"
        )
        message2 = Message.objects.create(
            chat_room=self.chat_room, sender=self.user2, content="Second message"
        )

        messages = Message.objects.all()
        # First message should be first
        self.assertEqual(messages[0], message1)
        self.assertEqual(messages[1], message2)

    def test_message_string_representation(self):
        """Test the string representation of a message"""
        message = Message.objects.create(
            chat_room=self.chat_room,
            sender=self.user1,
            content="This is a very long message that should be truncated in the string representation",
        )

        self.assertTrue(str(message).startswith(f"{self.user1.username}:"))
        self.assertTrue(len(str(message)) <= 100)  # Ensure truncation

    def test_empty_message_content(self):
        """Test that empty message content raises validation error"""
        with self.assertRaises(ValidationError):
            message = Message(chat_room=self.chat_room, sender=self.user1, content="")
            message.full_clean()
