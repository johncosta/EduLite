from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from chat.models import ChatRoom, Message


class ChatRoomTestModel(TestCase):
    """ Test cases for the ChatRoom model. """

    def setUp(self):
        """ test data for test multiple test methods """

        self.user1 = User.objects.create_user(
            username='testuser1',
            email='user1@example.com',
            password='password123',
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='user2@example.com',
            password='password123',
        )

    def test_create_one_to_one_chat(self):
        """Test creating a one-to-one chat room"""
        chat_room = ChatRoom.objects.create(
            name="One to One Chat",
            room_type='ONE_TO_ONE'
        )
        chat_room.participants.add(self.user1, self.user2)

        self.assertEqual(chat_room.room_type, 'ONE_TO_ONE')
        self.assertEqual(chat_room.participants.count(), 2)
        self.assertIn(self.user1, chat_room.participants.all())
        self.assertIn(self.user2, chat_room.participants.all())

    def test_create_group_chat(self):
        """Test creating a group chat room"""
        chat_room = ChatRoom.objects.create(
            name="Group Chat",
            room_type='GROUP'
        )
        chat_room.participants.add(self.user1, self.user2)

        self.assertEqual(chat_room.room_type, 'GROUP')
        self.assertEqual(chat_room.participants.count(), 2)

    def test_create_course_chat(self):
        """Test creating a course chat room"""
        chat_room = ChatRoom.objects.create(
            name="Course Discussion",
            room_type='COURSE'
        )
        chat_room.participants.add(self.user1, self.user2)

        self.assertEqual(chat_room.room_type, 'COURSE')
        self.assertEqual(chat_room.participants.count(), 2)

