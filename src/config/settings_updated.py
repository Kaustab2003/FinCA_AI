"""
FinCA AI - Application Settings
Loads environment variables and provides configuration management
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application configuration settings"""
    
    # App Configuration
    APP_NAME: str = Field(default="FinCA_AI", env="APP_NAME")
    APP_ENV: str = Field(default="development", env="APP_ENV")
    DEBUG: bool = Field(default=True, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    
    # Supabase
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL")
    SUPABASE_ANON_KEY: str = Field(..., env="SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_KEY: str = Field(..., env="SUPABASE_SERVICE_KEY")
    SUPABASE_JWT_SECRET: str = Field(..., env="SUPABASE_JWT_SECRET")
    
    # Database
    DATABASE_URL: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")
    
    # OpenAI (Legacy - kept for fallback)
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_EMBEDDING_MODEL: str = Field(default="text-embedding-3-small", env="OPENAI_EMBEDDING_MODEL")
    
    # DeepSeek (FREE - Primary AI)
    DEEPSEEK_API_KEY: Optional[str] = Field(default=None, env="DEEPSEEK_API_KEY")
    USE_DEEPSEEK: bool = Field(default=True, env="USE_DEEPSEEK")
    
    # Groq (FREE - Ultra Fast)
    GROQ_API_KEY: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    USE_GROQ: bool = Field(default=False, env="USE_GROQ")
    
    # AI Provider Priority: groq > deepseek > openai
    def get_ai_provider(self):
        """Get the best available AI provider"""
        if self.USE_GROQ and self.GROQ_API_KEY:
            return "groq"
        elif self.USE_DEEPSEEK and self.DEEPSEEK_API_KEY:
            return "deepseek"
        elif self.OPENAI_API_KEY:
            return "openai"
        return "fallback"
    
    # LangSmith
    LANGCHAIN_TRACING_V2: bool = Field(default=True, env="LANGCHAIN_TRACING_V2")
    LANGCHAIN_API_KEY: str = Field(..., env="LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT: str = Field(default="finca-ai-prod", env="LANGCHAIN_PROJECT")
    
    # Account Aggregator (Setu)
    AA_CLIENT_ID: Optional[str] = Field(default=None, env="AA_CLIENT_ID")
    AA_CLIENT_SECRET: Optional[str] = Field(default=None, env="AA_CLIENT_SECRET")
    AA_BASE_URL: str = Field(default="https://sandbox.setu.co", env="AA_BASE_URL")
    AA_REDIRECT_URL: str = Field(default="http://localhost:5000/aa/callback", env="AA_REDIRECT_URL")
    
    # News API
    NEWS_API_KEY: Optional[str] = Field(default=None, env="NEWS_API_KEY")
    NEWS_API_BASE: str = Field(default="https://newsapi.org/v2", env="NEWS_API_BASE")
    NEWS_FETCH_INTERVAL: int = Field(default=3600, env="NEWS_FETCH_INTERVAL")
    
    # Voice Services
    ENABLE_VOICE: bool = Field(default=True, env="ENABLE_VOICE")
    WHISPER_MODEL: str = Field(default="base", env="WHISPER_MODEL")
    WHISPER_USE_LOCAL: bool = Field(default=True, env="WHISPER_USE_LOCAL")
    
    # Security
    ENCRYPTION_KEY: Optional[str] = Field(default=None, env="ENCRYPTION_KEY")
    
    # Feature Flags
    ENABLE_GAMIFICATION: bool = Field(default=True, env="ENABLE_GAMIFICATION")
    ENABLE_SOCIAL: bool = Field(default=False, env="ENABLE_SOCIAL")
    ENABLE_AA: bool = Field(default=False, env="ENABLE_AA")
    ENABLE_PORTFOLIO_TRACKING: bool = Field(default=True, env="ENABLE_PORTFOLIO_TRACKING")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
