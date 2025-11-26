"""
Base Agent class for all specialized financial agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()

@dataclass
class AgentResponse:
    """Standardized response from agents"""
    content: str
    agent_name: str
    agent_type: str
    confidence: float = 1.0
    tools_used: list = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tools_used is None:
            self.tools_used = []
        if self.metadata is None:
            self.metadata = {}

class BaseAgent(ABC):
    """Abstract base class for all financial agents"""
    
    def __init__(self, model: str = "gpt-4o"):
        """
        Initialize agent with OpenAI model
        
        Args:
            model: OpenAI model name
        """
        self.model = model
        self.agent_name = self.__class__.__name__
        self.agent_type = self._get_agent_type()
        logger.info(f"Initialized {self.agent_name} with model {model}")
    
    @abstractmethod
    def _get_agent_type(self) -> str:
        """Return agent type identifier"""
        pass
    
    @abstractmethod
    async def process(self, query: str, user_context: Dict[str, Any]) -> AgentResponse:
        """
        Process user query with context
        
        Args:
            query: User's question/request
            user_context: User context including budget, goals, etc.
        
        Returns:
            AgentResponse with answer and metadata
        """
        pass
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for the agent"""
        return f"""You are a {self.agent_name}, a helpful financial assistant for young Indian professionals.
        
Your role: Provide accurate, personalized financial advice in simple language.
Tone: Friendly, encouraging, non-judgmental
Format: Use bullet points, emojis, and clear sections
Numbers: Always use Indian number format (₹1,00,000 not ₹100,000)"""
    
    def _format_currency(self, amount: float) -> str:
        """Format amount in Indian currency format"""
        if amount >= 10000000:  # 1 Crore+
            return f"₹{amount/10000000:.2f}Cr"
        elif amount >= 100000:  # 1 Lakh+
            return f"₹{amount/100000:.2f}L"
        else:
            return f"₹{amount:,.0f}"
