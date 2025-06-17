from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import ChatRoom, Message
from .serializers import MessageSerializer, ChatRoomSerializer
from .permissions import IsParticipant, IsMessageSenderOrReadOnly
from .pagination import ChatRoomPagination, MessageCursorPagination


class ChatAppBaseAPIView(APIView):
    """
    A custom base API view for the Chat app.
    Provides default authentication permissions and a helper method to get serializer context.
    Other common functionalities for Chat APIViews can be added here.

    **attribute** 'permission_classes' is set to [IsAuthenticated] by default.
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        """
        Ensures that the request object is available to the serializer context.
        """
        return {"request": self.request}


class ChatRoomListCreateView(ChatAppBaseAPIView):
    """
    API view to list chat rooms the authenticated user is part of or create a new chat room.
    - GET: Returns a paginated list of chat rooms where user is a participant
    - POST: Creates a new chat room and adds creator as participant
    """
    permission_classes = [IsAuthenticated, IsParticipant]
    pagination_class = ChatRoomPagination

    def get(self, request):
        """List chat rooms where user is a participant"""
        queryset = ChatRoom.objects.filter(participants=request.user)

        # Handle pagination
        page = self.pagination_class().paginate_queryset(queryset, request)
        if page is not None:
            serializer = ChatRoomSerializer(page, many=True, context=self.get_serializer_context())
            return self.pagination_class().get_paginated_response(serializer.data)

        serializer = ChatRoomSerializer(queryset, many=True, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Create a new chat room and add creator as participant"""
        serializer = ChatRoomSerializer(data=request.data, context=self.get_serializer_context())
        if serializer.is_valid():
            chat_room = serializer.save()
            chat_room.participants.add(request.user)
            return Response(
                ChatRoomSerializer(chat_room, context=self.get_serializer_context()).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatRoomDetailView(ChatAppBaseAPIView):
    """
    API view to retrieve details for a specific chat room.
    - GET: Returns details of a chat room if user is a participant
    """
    permission_classes = [IsAuthenticated, IsParticipant]
    
    def get_object(self, pk):
        """Helper method to retrieve the chat room object or raise a 404 error"""
        return get_object_or_404(ChatRoom.objects.all(), pk=pk)

    def get(self, request, pk):
        """Retrieve details of a specific chat room"""
        chat_room = self.get_object(pk)
        self.check_object_permissions(request, chat_room)
        serializer = ChatRoomSerializer(chat_room, context=self.get_serializer_context())
        return Response(serializer.data)


class MessageListCreateView(ChatAppBaseAPIView):
    """
    API view to list and create messages in a specific chat room.
    - GET: Returns a paginated list of messages in a chat room
    - POST: Creates a new message in the chat room
    """
    permission_classes = [IsAuthenticated, IsMessageSenderOrReadOnly]
    pagination_class = MessageCursorPagination

    def get_chat_room(self, chat_room_id):
        """Helper method to retrieve the chat room object"""
        return get_object_or_404(
            ChatRoom.objects.all(),
            id=chat_room_id,
            participants=self.request.user
        )

    def get(self, request, chat_room_id):
        """List messages for a specific chat room"""
        # Verify chat room exists and user is participant
        chat_room = self.get_chat_room(chat_room_id)
        
        queryset = Message.objects.filter(
            chat_room=chat_room
        ).select_related("sender", "chat_room")
        
        # Handle pagination
        page = self.pagination_class().paginate_queryset(queryset, request)
        if page is not None:
            serializer = MessageSerializer(page, many=True, context=self.get_serializer_context())
            return self.pagination_class().get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(queryset, many=True, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, chat_room_id):
        """Create a new message in the chat room"""
        # Verify chat room exists and user is participant
        chat_room = self.get_chat_room(chat_room_id)
        
        serializer = MessageSerializer(data=request.data, context=self.get_serializer_context())
        if serializer.is_valid():
            message = serializer.save(
                chat_room=chat_room,
                sender=request.user
            )
            return Response(
                MessageSerializer(message, context=self.get_serializer_context()).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


""" Retrieve a specific message in a chat room (Message sender can update/delete)"""


class MessageDetailView(ChatAppBaseAPIView):
    """
    API view to manage a specific message in a chat room.
    - GET: Retrieve a specific message
    - PUT: Update a message (sender only)
    - PATCH: Partially update a message (sender only)
    - DELETE: Delete a message (sender only)
    """
    permission_classes = [IsAuthenticated, IsMessageSenderOrReadOnly]

    def get_object(self, chat_room_id, message_id):
        """Helper method to retrieve the message object or raise a 404 error"""
        return get_object_or_404(
            Message.objects.select_related("sender", "chat_room"),
            id=message_id,
            chat_room__id=chat_room_id,
            chat_room__participants=self.request.user
        )

    def get(self, request, chat_room_id, pk):
        """Retrieve a specific message"""
        message = self.get_object(chat_room_id, pk)
        serializer = MessageSerializer(message, context=self.get_serializer_context())
        return Response(serializer.data)

    def put(self, request, chat_room_id, pk):
        """Update a message (full update)"""
        message = self.get_object(chat_room_id, pk)
        self.check_object_permissions(request, message)
        
        serializer = MessageSerializer(
            message,
            data=request.data,
            context=self.get_serializer_context()
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, chat_room_id, pk):
        """Update a message (partial update)"""
        message = self.get_object(chat_room_id, pk)
        self.check_object_permissions(request, message)
        
        serializer = MessageSerializer(
            message,
            data=request.data,
            partial=True,
            context=self.get_serializer_context()
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, chat_room_id, pk):
        """Delete a message"""
        message = self.get_object(chat_room_id, pk)
        self.check_object_permissions(request, message)
        message.delete()
        return Response(
            {"message": "Message deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
