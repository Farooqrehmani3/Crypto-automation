"""
Supabase Client Integration

Provides both admin (service_role) and client-level access to Supabase services:
- Database queries (via service_role for backend operations)
- Auth verification (JWT validation)
- Realtime subscriptions (via Python client)
- Storage access
"""

from typing import Optional

from supabase import create_client, Client
from structlog import get_logger

from app.core.config import settings

logger = get_logger(__name__)


class SupabaseService:
    """Supabase integration service with admin privileges."""

    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.service_key = settings.SUPABASE_SERVICE_ROLE_KEY
        self.anon_key = settings.SUPABASE_ANON_KEY
        self.jwt_secret = settings.SUPABASE_JWT_SECRET
        self._admin_client: Optional[Client] = None
        self._anon_client: Optional[Client] = None

    @property
    def admin(self) -> Client:
        """Get Supabase client with service_role (admin) privileges.
        Use this for backend operations that need to bypass RLS.
        """
        if self._admin_client is None:
            if not self.url or not self.service_key:
                raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
            self._admin_client = create_client(self.url, self.service_key)
            logger.info("Supabase admin client initialized")
        return self._admin_client

    @property
    def anon(self) -> Client:
        """Get Supabase client with anon key (public) privileges.
        Use this for operations that should respect RLS.
        """
        if self._anon_client is None:
            if not self.url or not self.anon_key:
                raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")
            self._anon_client = create_client(self.url, self.anon_key)
            logger.info("Supabase anon client initialized")
        return self._anon_client

    async def verify_token(self, token: str) -> Optional[dict]:
        """Verify a Supabase JWT token and return user info."""
        try:
            # Use the admin client to verify the token
            user = self.admin.auth.get_user(token)
            if user and user.user:
                return {
                    "id": user.user.id,
                    "email": user.user.email,
                    "created_at": user.user.created_at,
                    "phone": user.user.phone,
                }
            return None
        except Exception as e:
            logger.warning("Token verification failed", error=str(e))
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user information from Supabase Auth."""
        try:
            response = self.admin.auth.admin.get_user_by_id(user_id)
            if response and response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "created_at": response.user.created_at,
                    "phone": response.user.phone,
                    "user_metadata": response.user.user_metadata,
                }
            return None
        except Exception as e:
            logger.error("Failed to get user", user_id=user_id, error=str(e))
            return None


# Singleton
supabase_service = SupabaseService()
