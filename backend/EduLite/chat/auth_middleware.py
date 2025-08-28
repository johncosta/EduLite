import logging
from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware

User = get_user_model()
logger = logging.getLogger(__name__)

@database_sync_to_async
def get_user_from_jwt(token_key: str):
    """
    Get user from JWT token
    
    Args:
        token_key: JWT token key
        
    Returns:
        User instance or AnonymousUser
    """
    try:
        # Validate JWT token
        validated_token = UntypedToken(token_key)
        user_id = validated_token['user_id']
        
        # Get user from database
        user = User.objects.get(id=user_id, is_active=True)
        return user
        
    except (InvalidToken, TokenError, User.DoesNotExist) as e:
        logger.warning(f"JWT authentication failed: {str(e)}")
        return AnonymousUser()
    except Exception as e:
        logger.error(f"Unexpected JWT authentication error: {str(e)}")
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """
    Middleware to authenticate WebSocket connections using JWT tokens.
    
    Supports both header-based and query parameter-based token authentication.
    """

    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        """
        Authenticate WebSocket connection during handshake.
        
        Args:
            scope: ASGI scope containing connection information
            receive: ASGI receive callable
            send: ASGI send callable
        """
        # only process WebSocket connections
        if scope['type'] == 'websocket':
            token = await self.get_token_from_scope(scope)

            if token:
                scope['user'] = await get_user_from_jwt(token)
            else:
                scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)
    
    async def get_token_from_scope(self, scope):
        """
        Extract JWT token from WebSocket scope.
        
        Args:
            scope: ASGI scope
            
        Returns:
            Token string or None
        """
        # Method 1: Check Authorization header
        headers = dict(scope.get('headers', []))
        if b'authorization' in headers:
            try:
                auth_header = headers[b'authorization'].decode()
                token_type, token = auth_header.split()
                if token_type.lower() == 'bearer':
                    return token
            except (ValueError, UnicodeDecodeError):
                pass

        # Method 2: Check query parameters  
        query_string = scope.get('query_string', b'').decode()
        if query_string:
            query_params = parse_qs(query_string)
            token = query_params.get('token', [None])[0]
            if token:
                return token

        return None
    
def JWTAuthMiddlewareStack(inner):
    """
    Create JWT authentication middleware stack.
    
    Args:
        inner: Inner ASGI application
        
    Returns:
        Middleware stack with JWT authentication
    """
    return JWTAuthMiddleware(inner)