# courses/tests/test_CourseChatRoom.py
# Tests for the CourseChatRoom model

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from ..models import Course, CourseChatRoom
from chat.models import ChatRoom

User = get_user_model()


class CourseChatRoomTest(TestCase):
    """
    Unit tests for the CourseChatRoom model.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """
        Set up reusable test data: users, courses, and chat rooms.
        """
        cls.user1 = User.objects.create_user(
            username="testuser1", password="password123", email="testuser1@example.com"
        )
        cls.user2 = User.objects.create_user(
            username="testuser2", password="password123", email="testuser2@example.com"
        )
        cls.course1 = Course.objects.create(title="test_course1")
        cls.course2 = Course.objects.create(title="test_course2")
        cls.chat_room1 = ChatRoom.objects.create(
            name="test_chat_room1", room_type="ONE_TO_ONE"
        )
        cls.chat_room2 = ChatRoom.objects.create(
            name="test_chat_room2", room_type="GROUP"
        )

    def test_course_chat_room_creation(self) -> None:
        """
        Test that a CourseChatRoom is successfully created.
        """
        chat_link = CourseChatRoom.objects.create(
            course=self.course1,
            chatroom=self.chat_room1,
            created_by=self.user1,
        )
        chat_link.full_clean()
        self.assertEqual(chat_link.course, self.course1)
        self.assertEqual(chat_link.chatroom, self.chat_room1)
        self.assertEqual(chat_link.created_by, self.user1)

    def test_course_chat_room_str(self) -> None:
        """
        Test the string representation of CourseChatRoom.
        """
        chat_link = CourseChatRoom.objects.create(
            course=self.course1,
            chatroom=self.chat_room1,
            created_by=self.user1,
        )
        expected_str = f"{self.course1.title} - {self.chat_room1.name}"
        self.assertEqual(str(chat_link), expected_str)

    def test_course_chat_room_delete(self) -> None:
        """
        Test that CourseChatRoom is deleted properly.
        """
        chat_link = CourseChatRoom.objects.create(
            course=self.course1,
            chatroom=self.chat_room1,
            created_by=self.user1,
        )
        chat_link_id = chat_link.id
        chat_link.delete()
        self.assertFalse(CourseChatRoom.objects.filter(pk=chat_link_id).exists())

    def test_course_chat_room_update(self) -> None:
        """
        Test updating the course and chatroom fields of CourseChatRoom.
        """
        chat_link = CourseChatRoom.objects.create(
            course=self.course1,
            chatroom=self.chat_room1,
            created_by=self.user1,
        )
        chat_link.course = self.course2
        chat_link.chatroom = self.chat_room2
        chat_link.save()

        self.assertEqual(chat_link.course, self.course2)
        self.assertEqual(chat_link.chatroom, self.chat_room2)

    def test_course_chat_room_invalid_user(self) -> None:
        """
        Test that modifying `created_by` raises a ValidationError.
        """
        chat_link = CourseChatRoom.objects.create(
            course=self.course1,
            chatroom=self.chat_room1,
            created_by=self.user1,
        )
        chat_link.created_by = self.user2
        with self.assertRaises(ValidationError):
            chat_link.full_clean()

    def test_user_delete_cascade(self) -> None:
        """
        Test that deleting a user deletes related CourseChatRoom.
        """
        chat_link = CourseChatRoom.objects.create(
            course=self.course1,
            chatroom=self.chat_room1,
            created_by=self.user1,
        )
        chat_link_id = chat_link.id
        self.user1.delete()
        self.assertFalse(CourseChatRoom.objects.filter(pk=chat_link_id).exists())

    def test_course_delete_cascade(self) -> None:
        """
        Test that deleting a course deletes related CourseChatRoom.
        """
        chat_link = CourseChatRoom.objects.create(
            course=self.course1,
            chatroom=self.chat_room1,
            created_by=self.user1,
        )
        chat_link_id = chat_link.id
        self.course1.delete()
        self.assertFalse(CourseChatRoom.objects.filter(pk=chat_link_id).exists())

    def test_chatroom_delete_cascade(self) -> None:
        """
        Test that deleting a chatroom deletes related CourseChatRoom.
        """
        chat_link = CourseChatRoom.objects.create(
            course=self.course1,
            chatroom=self.chat_room1,
            created_by=self.user1,
        )
        chat_link_id = chat_link.id
        self.chat_room1.delete()
        self.assertFalse(CourseChatRoom.objects.filter(pk=chat_link_id).exists())
