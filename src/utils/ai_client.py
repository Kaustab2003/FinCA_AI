"""
AI Client Wrapper - Supports OpenAI, DeepSeek, and Groq
"""
from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI
from src.config.settings import settings
from src.utils.logger import logger


class AIClient:
    """Universal AI client that works with OpenAI, DeepSeek, and Groq"""
    
    def __init__(self):
        self.provider = settings.get_ai_provider()
        self.client = None
        self.model = None
        
        logger.info(f"Initializing AI client with provider: {self.provider}")
        
        if self.provider == "groq":
            self._init_groq()
        elif self.provider == "deepseek":
            self._init_deepseek()
        elif self.provider == "openai":
            self._init_openai()
        else:
            logger.warning("No AI provider available, using fallback mode")
    
    def _init_groq(self):
        """Initialize Groq client (FREE & FAST)"""
        try:
            self.client = AsyncOpenAI(
                api_key=settings.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1"
            )
            # Groq models: llama-3.3-70b-versatile (best), mixtral-8x7b-32768
            self.model = "llama-3.3-70b-versatile"
            logger.info("✅ Groq AI initialized successfully")
        except Exception as e:
            logger.error(f"Groq initialization failed: {e}")
            self._fallback_to_next()
    
    def _init_deepseek(self):
        """Initialize DeepSeek client (FREE)"""
        try:
            self.client = AsyncOpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com"
            )
            self.model = "deepseek-chat"
            logger.info("✅ DeepSeek AI initialized successfully")
        except Exception as e:
            logger.error(f"DeepSeek initialization failed: {e}")
            self._fallback_to_next()
    
    def _init_openai(self):
        """Initialize OpenAI client (PAID)"""
        try:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = "gpt-4o-mini"
            logger.info("✅ OpenAI initialized successfully")
        except Exception as e:
            logger.error(f"OpenAI initialization failed: {e}")
            self.provider = "fallback"
    
    def _fallback_to_next(self):
        """Try next available provider"""
        if self.provider == "groq" and settings.DEEPSEEK_API_KEY:
            self.provider = "deepseek"
            self._init_deepseek()
        elif self.provider == "deepseek" and settings.OPENAI_API_KEY:
            self.provider = "openai"
            self._init_openai()
        else:
            self.provider = "fallback"
            logger.warning("All AI providers failed, using fallback mode")
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.5,
        max_tokens: int = 1200
    ) -> Optional[str]:
        """Get chat completion from AI provider"""
        if not self.client:
            raise Exception("No AI provider available")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            raise
    
    async def generate_response(
        self, 
        prompt: str, 
        model: str = None,
        temperature: float = 0.5,
        max_tokens: int = 1200
    ) -> str:
        """Generate response from prompt (convenience method)"""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(messages, temperature, max_tokens)
    
    def is_available(self) -> bool:
        """Check if AI provider is available"""
        return self.client is not None and self.provider != "fallback"
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about current provider"""
        return {
            "provider": self.provider,
            "model": self.model,
            "is_free": self.provider in ["groq", "deepseek"],
            "is_available": self.is_available()
        }
