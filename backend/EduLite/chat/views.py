from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import ChatRoom, Message
from .serializers import (MessageSerializer, ChatRoomSerializer)
from .permissions import IsParticipant, IsMessageSenderOrReadOnly
from .pagination import ChatRoomPagination, MessageCursorPagination

# Create your views here.

""" List chat rooms the authenticated user is part of """

class ChatRoomListView(generics.ListCreateAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated, IsParticipant]
    pagination_class = ChatRoomPagination

    def get_queryset(self):
        # Return chat rooms where the user is a participant
        return ChatRoom.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        # Add the creator as a participant
        chat_room = serializer.save()
        chat_room.participants.add(self.request.user)


""" Retrieve details for a specific chat room (if user is a participant)"""


class ChatRoomDetailView(generics.RetrieveAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated, IsParticipant]

    def get_queryset(self):
        return ChatRoom.objects.all()


""" List and Create Messages in a specific chat room """

class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsMessageSenderOrReadOnly]
    pagination_class = MessageCursorPagination

    def get_queryset(self):
        # Return messages for the given chat room if user is a participant
        chat_room_id = self.kwargs['chat_room_id']
        return Message.objects.filter(
            chat_room__id=chat_room_id,
            chat_room__participants=self.request.user
        ).select_related('sender', 'chat_room')

    def perform_create(self, serializer):
        # Ensure only participants can send messages and set sender
        chat_room_id = self.kwargs['chat_room_id']
        chat_room = ChatRoom.objects.get(
            id=chat_room_id,
            participants=self.request.user
        )
        serializer.save(chat_room=chat_room, sender=self.request.user)


""" Retrieve a specific message in a chat room (Message sender can update/delete)"""

class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsMessageSenderOrReadOnly]

    def get_queryset(self):
        chat_room_id = self.kwargs['chat_room_id']
        return Message.objects.filter(
            chat_room__id=chat_room_id,
            chat_room__participants=self.request.user
        ).select_related('sender', 'chat_room')
