# backend/EduLite/urls.py

from django.contrib import admin
from django.urls import path, include # Make sure include is imported

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),  # Include your app's URLs under the 'api/' prefix
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')), # For browsable API login/logout
]