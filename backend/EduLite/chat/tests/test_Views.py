import logging

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from chat.models import ChatRoom, Message
from chat.serializers import ChatRoomSerializer, MessageSerializer

logger = logging.getLogger(__name__)

class ChatRoomViewsTest(APITestCase):
    """Test suite for ChatRoom views custom logic"""

    def setUp(self):
        """Set up test data"""
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1', 
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2', 
            password='testpass123'
        )
        
        # Create test chat room
        self.chat_room = ChatRoom.objects.create(
            name="Test Room",
            room_type='ONE_TO_ONE'
        )
        self.chat_room.participants.add(self.user1, self.user2)

        # URLs
        self.list_url = reverse('chat-room-list')
        self.detail_url = reverse('chat-room-detail', kwargs={'pk': self.chat_room.pk})

    def test_list_rooms_participant_filter(self):
        """Test that get_queryset filters rooms by participant"""
        # Create another room where user1 is not a participant
        other_room = ChatRoom.objects.create(
            name="Other Room",
            room_type='GROUP'
        )
        other_room.participants.add(self.user2)

        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.chat_room.id)

    def test_create_room_adds_creator(self):
        # TODO: Add a new field to the model for creator=ForeignKey(User)
        #  - This should enable the creator to do things like add/remove participants
        #  - and change room name/info
        #     - Perhaps we can add a new editors field as well, for users who can edit
        """Test that perform_create adds creator as participant"""
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'New Chat Room',
            'room_type': 'GROUP'
        }
        response = self.client.post(self.list_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_room = ChatRoom.objects.get(id=response.data['id'])
        self.assertTrue(new_room.participants.filter(id=self.user1.id).exists())
        
    def test_create_room_and_add_other_participant(self):
        # TODO: Add a 'invite' way to add other participants
        # - We can still allow API consumers to add "participants" [id1, id2, id3]
        # - but instead of adding them to the room,
        # - it should send an 'invite' notification to each participant
        # - the participant should be able to accept/reject the invite
        #   - also, we can generate an `invite-slug` and create a link
        #   - chatroom creators can share that link with participants
        #   - perhaps `invite-slug` can be part of the ChatRoom model itself
        
        """Test that perform_create adds other participants"""
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'New Chat Room',
            'room_type': 'GROUP',
            'participants': [self.user2.id]
        }
        response = self.client.post(self.list_url, data)
        
        logger.debug(
            f"test_create_room_and_add_other_participant():\n"
            f"---\n"
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        new_room = ChatRoom.objects.get(id=response.data['id'])
        
        logger.debug(
            f"--\tNew room: {new_room}\n"
            f"--\tParticipants: {new_room.participants.all()}\n"
        )
        
        self.assertTrue(new_room.participants.filter(id=self.user1.id).exists())
        self.assertTrue(new_room.participants.filter(id=self.user2.id).exists())

class MessageViewsTest(APITestCase):
    """Test suite for Message views custom logic"""
    # TODO: Feature - Message Reactions (Initial thought for future tests)
    #   - Consider adding a `Reaction` model related to `Message`.
    #   - Future tests would cover:
    #     - Adding a reaction to a message.
    #     - Removing a reaction.
    #     - Listing reactions for a message.
    #     - Ensuring users can only react once with the same emoji (or defining reaction rules).
    #   - This might take place in a seperate MessageReactionTest class/file.

    def setUp(self):
        """Set up test data"""
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1', 
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2', 
            password='testpass123'
        )
        self.non_participant = User.objects.create_user(
            username='nonparticipant', 
            password='testpass123'
        )
        
        # Create test chat room
        self.chat_room = ChatRoom.objects.create(
            name="Test Room",
            room_type='ONE_TO_ONE'
        )
        self.chat_room.participants.add(self.user1, self.user2)

        # Create test message
        self.message = Message.objects.create(
            content="Test message",
            chat_room=self.chat_room,
            sender=self.user1
        )

        # URLs
        self.message_list_url = reverse('message-list-create', 
            kwargs={'chat_room_id': self.chat_room.pk})
        self.message_detail_url = reverse('message-detail', 
            kwargs={
                'chat_room_id': self.chat_room.pk,
                'pk': self.message.pk
            })

    def test_message_queryset_participant_filter(self):
        """Test that get_queryset filters messages by participant"""
        self.client.force_authenticate(user=self.non_participant)
        response = self.client.get(self.message_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)        
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.message_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['results']) > 0)

    def test_create_message_sets_sender_and_room(self):
        """Test that perform_create sets sender and chat_room"""
        self.client.force_authenticate(user=self.user1)
        data = {'content': 'New test message'}
        response = self.client.post(self.message_list_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['sender'], 'testuser1')
        self.assertEqual(response.data['chat_room'], self.chat_room.id)

    def test_create_message_non_participant(self):
        """Test that non-participants cannot create messages"""
        self.client.force_authenticate(user=self.non_participant)
        data = {'content': 'New test message'}
        response = self.client.post(self.message_list_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
