# backend/users/urls.py

from django.urls import path
from . import views 

urlpatterns = [
    # User URLs
    path('users/', views.UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', views.UserRetrieveUpdateDestroyView.as_view(), name='user-detail'),

    # Group URLs
    path('groups/', views.GroupListCreateView.as_view(), name='group-list-create'),
    path('groups/<int:pk>/', views.GroupRetrieveUpdateDestroyView.as_view(), name='group-detail'),
]