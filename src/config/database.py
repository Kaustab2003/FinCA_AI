"""
Database connection and client initialization for Supabase
"""
from supabase import create_client, Client
from src.config.settings import settings
import structlog
from typing import Optional
from contextlib import contextmanager

logger = structlog.get_logger()

class DatabaseClient:
    """Supabase database client wrapper with improved connection management"""

    _instance: Optional[Client] = None
    _service_instance: Optional[Client] = None
    _authenticated: bool = False

    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client instance with connection reuse"""
        if cls._instance is None:
            try:
                cls._instance = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_ANON_KEY
                )
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                raise
        return cls._instance

    @classmethod
    def get_authenticated_client(cls) -> Client:
        """Get authenticated Supabase client instance"""
        client = cls.get_client()
        if not cls._authenticated:
            logger.warning("Database client is not authenticated. RLS policies may block operations.")
        return client

    @classmethod
    def authenticate_client(cls, access_token: str, refresh_token: str = None) -> bool:
        """Authenticate the client with user tokens"""
        try:
            client = cls.get_client()
            # Set the session manually
            client.auth.set_session(access_token, refresh_token)
            cls._authenticated = True
            logger.info("Database client authenticated successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to authenticate database client: {e}")
            cls._authenticated = False
            return False

    @classmethod
    def sign_out_client(cls) -> None:
        """Sign out the authenticated client"""
        try:
            if cls._instance:
                cls._instance.auth.sign_out()
            cls._authenticated = False
            logger.info("Database client signed out")
        except Exception as e:
            logger.error(f"Failed to sign out database client: {e}")

    @classmethod
    def get_service_client(cls) -> Client:
        """Get Supabase client with service role key (admin access)"""
        if cls._service_instance is None:
            try:
                cls._service_instance = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_SERVICE_KEY
                )
                logger.info("Supabase service client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase service client: {e}")
                raise
        return cls._service_instance

    @classmethod
    def reset_clients(cls):
        """Reset client instances (useful for testing or connection issues)"""
        cls._instance = None
        cls._service_instance = None
        cls._authenticated = False
        logger.info("Supabase clients reset")

    @classmethod
    @contextmanager
    def get_temp_client(cls):
        """Get a temporary client instance (auto-cleanup)"""
        client = None
        try:
            client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_ANON_KEY
            )
            yield client
        finally:
            if client:
                # Supabase client doesn't need explicit cleanup
                pass

# Global client instance
supabase = DatabaseClient.get_client()
