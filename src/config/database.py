"""
Database connection and client initialization for Supabase
"""
from supabase import create_client, Client
from src.config.settings import settings
import structlog

logger = structlog.get_logger()

class DatabaseClient:
    """Supabase database client wrapper"""
    
    _instance: Client = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client instance"""
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
    def get_service_client(cls) -> Client:
        """Get Supabase client with service role key (admin access)"""
        try:
            return create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_KEY
            )
        except Exception as e:
            logger.error(f"Failed to initialize Supabase service client: {e}")
            raise

# Global client instance
supabase = DatabaseClient.get_client()
