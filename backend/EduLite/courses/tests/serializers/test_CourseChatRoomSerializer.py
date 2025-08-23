from django.test import TestCase
from rest_framework.validators import ValidationError
from django.contrib.auth import get_user_model

from ...serializers import CourseChatRoomSerializer
from ...models import CourseChatRoom, Course
from chat.models import ChatRoom

User = get_user_model()

class CourseChatRoomSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test users
        cls.user1 = User.objects.create_user(
            username="testuser1", password="password123", email="testuser1@example.com"
        )
        cls.user2 = User.objects.create_user(
            username="testuser2", password="password123", email="testuser2@example.com"
        )
        cls.course1 = Course.objects.create(title="test_course1")
        cls.chat_room1 = ChatRoom.objects.create(
            name="test_chat_room1", room_type="ONE_TO_ONE"
        )
        cls.course_chat_room = CourseChatRoom.objects.create(
            course=cls.course1,
            chatroom=cls.chat_room1,
            created_by=cls.user1,
        )
    
    def test_serializer_contains_all_fields(self):
        serializer = CourseChatRoomSerializer(instance=self.course_chat_room)
        data = serializer.data

        self.assertEqual(data['id'], self.course_chat_room.id)
        self.assertEqual(data['course'], self.course_chat_room.course.id)
        self.assertEqual(data['course_title'], self.course_chat_room.course.title)
        self.assertEqual(data['chatroom'], self.course_chat_room.chatroom.id)
        self.assertEqual(data['chatroom_name'], self.course_chat_room.chatroom.name)
        self.assertEqual(data['created_by'], self.course_chat_room.created_by.id)
        self.assertEqual(data['created_user_name'], self.course_chat_room.created_by.username)

    def test_read_only_created_by_is_ignored_on_input(self):
        data = {
            "course": self.course1.id,
            "chatroom": self.chat_room1.id,
            "created_by": self.user1.id  # This should be ignored
        }
        serializer = CourseChatRoomSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        assert "created_by" not in serializer.validated_data