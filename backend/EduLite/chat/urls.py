from django.urls import path
from . import views

urlpatterns = [
    # chat urls
    path('rooms/', views.ChatRoomListView.as_view(), name='chat-room-list'),
    path('rooms/<int:pk>/', views.ChatRoomDetailView.as_view(), name='chat-room-detail'),

    # messages urls
    path('rooms/<int:chat_room_id>/messages/', views.MessageListCreateView.as_view(), name='message-list-create'),
    path('rooms/<int:chat_room_id>/messages/<int:pk>/', views.MessageDetailView.as_view(), name='message-detail'),
]