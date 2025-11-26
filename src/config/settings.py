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
    
    # Monitoring
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    SENTRY_ENVIRONMENT: str = Field(default="development", env="SENTRY_ENVIRONMENT")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(default=0.1, env="SENTRY_TRACES_SAMPLE_RATE")
    SENTRY_SEND_DEFAULT_PII: bool = Field(default=True, env="SENTRY_SEND_DEFAULT_PII")
    SENTRY_TOKEN: Optional[str] = Field(default=None, env="SENTRY_TOKEN")
    PROMETHEUS_PORT: Optional[int] = Field(default=9090, env="PROMETHEUS_PORT")
    
    # Security
    ENCRYPTION_KEY: Optional[str] = Field(default=None, env="ENCRYPTION_KEY")
    JWT_EXPIRY_MINUTES: int = Field(default=1440, env="JWT_EXPIRY_MINUTES")
    CORS_ORIGINS: str = Field(default="http://localhost:5000,http://localhost:3000", env="CORS_ORIGINS")
    
    # Feature Flags
    ENABLE_GAMIFICATION: bool = Field(default=True, env="ENABLE_GAMIFICATION")
    ENABLE_PEER_COMPARISON: bool = Field(default=True, env="ENABLE_PEER_COMPARISON")
    ENABLE_VOICE_ASSISTANT: bool = Field(default=True, env="ENABLE_VOICE_ASSISTANT")
    ENABLE_ACCOUNT_AGGREGATOR: bool = Field(default=False, env="ENABLE_ACCOUNT_AGGREGATOR")
    ENABLE_RAG: bool = Field(default=True, env="ENABLE_RAG")
    ENABLE_SOCIAL: bool = Field(default=False, env="ENABLE_SOCIAL")
    ENABLE_AA: bool = Field(default=False, env="ENABLE_AA")
    ENABLE_PORTFOLIO_TRACKING: bool = Field(default=True, env="ENABLE_PORTFOLIO_TRACKING")
    
    # Rate Limiting
    API_RATE_LIMIT: int = Field(default=100, env="API_RATE_LIMIT")
    LLM_RATE_LIMIT: int = Field(default=20, env="LLM_RATE_LIMIT")
    
    # Compliance
    DATA_RETENTION_DAYS: int = Field(default=730, env="DATA_RETENTION_DAYS")
    GDPR_ENABLED: bool = Field(default=True, env="GDPR_ENABLED")
    AUDIT_LOG_ENABLED: bool = Field(default=True, env="AUDIT_LOG_ENABLED")
    
    # Stock Market API
    ALPHAVANTAGE_API_KEY: Optional[str] = Field(default=None, env="ALPHAVANTAGE_API_KEY")
    ALPHAVANTAGE_BASE_URL: str = Field(default="https://www.alphavantage.co/query", env="ALPHAVANTAGE_BASE_URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env


# Create global settings instance
settings = Settings()
