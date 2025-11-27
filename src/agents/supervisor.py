"""
SupervisorAgent - Routes user queries to specialized agents (Updated with Groq/DeepSeek)
"""
from typing import Dict, Any, Optional
import re
from src.agents.base_agent import BaseAgent, AgentResponse
from src.utils.ai_client import AIClient
from src.config.settings import settings
from src.utils.logger import logger


class SupervisorAgent(BaseAgent):
    """Routes queries to appropriate specialized agents"""
    
    def __init__(self):
        super().__init__()
        self.ai_client = AIClient()
        
        # Agent routing patterns
        self.routing_patterns = {
            'tax': [
                r'\b(tax|itr|income tax|tds|deduction|80c|80d|exemption|section)\b',
                r'\b(refund|rebate|assessment|form 16|form 26as)\b',
                r'\b(old regime|new regime|tax saving|tax planning)\b'
            ],
            'investment': [
                r'\b(invest|investment|stock|mutual fund|sip|portfolio|equity)\b',
                r'\b(fd|ppf|nps|elss|bonds|gold|debt fund|index fund)\b',
                r'\b(returns|allocation|diversification|risk|market|nifty|sensex)\b'
            ],
            'debt': [
                r'\b(loan|debt|emi|credit card|personal loan|home loan)\b',
                r'\b(interest rate|repay|refinance|prepayment|debt consolidation)\b',
                r'\b(credit score|cibil|default|outstanding|balance transfer)\b'
            ],
            'legal': [
                r'\b(legal|law|compliance|regulation|rbi|sebi|rera)\b',
                r'\b(contract|agreement|will|nominee|insurance claim)\b',
                r'\b(rights|consumer|fraud|complaint|dispute)\b'
            ]
        }
        
        provider_info = self.ai_client.get_provider_info()
        logger.info(f"Initialized SupervisorAgent with {provider_info['provider']} ({provider_info['model']})")
    
    def _get_agent_type(self) -> str:
        return "supervisor"
    
    def _detect_intent(self, query: str) -> str:
        """Detect which specialized agent to route to"""
        query_lower = query.lower()
        
        # Score each agent type
        scores = {}
        for agent_type, patterns in self.routing_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    score += 1
            scores[agent_type] = score
        
        # Return agent with highest score, default to investment
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return 'investment'  # Default for general financial queries
    
    def _use_llm_routing(self, query: str, user_context: Dict[str, Any]) -> str:
        """Use LLM for intelligent routing when pattern matching is unclear"""
        try:
            if not self.ai_client.is_available():
                return self._detect_intent(query)
            
            prompt = f"""You are a routing assistant for a financial advisor AI system.
Given the user query, determine which specialized agent should handle it.

Available agents:
- tax: Income tax, deductions, tax planning, ITR filing
- investment: Portfolio management, SIP, mutual funds, stocks, asset allocation
- debt: Loans, EMI, credit cards, debt management
- legal: Financial laws, compliance, rights, disputes

User query: "{query}"

Respond with ONLY the agent name (tax/investment/debt/legal)."""

            messages = [{"role": "user", "content": prompt}]
            
            response = self.ai_client.chat_completion(messages, temperature=0, max_tokens=10)
            
            agent = response.strip().lower()
            if agent in ['tax', 'investment', 'debt', 'legal']:
                return agent
            return 'investment'
            
        except Exception as e:
            logger.error("LLM routing failed", error=str(e))
            return self._detect_intent(query)
    
    async def process(self, query: str, user_context: Dict[str, Any]) -> AgentResponse:
        """Route query to appropriate agent with personal context"""
        try:
            # Detect intent
            agent_type = self._detect_intent(query)
            confidence = 0.8
            
            # Import specialized agents
            from src.agents.tax_agent import TaxCalculatorAgent
            from src.agents.investment_agent import InvestmentAdvisorAgent
            from src.agents.debt_agent import DebtManagerAgent
            from src.agents.legal_agent import LegalAssistantAgent
            
            # Route to specialized agent
            agent_map = {
                'tax': TaxCalculatorAgent(),
                'investment': InvestmentAdvisorAgent(),
                'debt': DebtManagerAgent(),
                'legal': LegalAssistantAgent()
            }
            
            specialized_agent = agent_map.get(agent_type)
            
            # Enhance user context with personal financial data
            enhanced_context = user_context.copy()
            personal_data = user_context.get('personal_finances', '')
            if personal_data:
                enhanced_context['system_prompt_addition'] = f"""
                User's personal financial data:
                {personal_data}
                
                Use this information to provide personalized advice.
                """
            
            logger.info("Routing query with personal context", 
                       agent_type=agent_type,
                       has_personal_data=bool(personal_data),
                       query_preview=query[:50])
            
            # Process with specialized agent using enhanced context
            response = await specialized_agent.process(query, enhanced_context)
            
            return AgentResponse(
                content=response.content,
                agent_name=f"Supervisor → {response.agent_name}",
                agent_type=agent_type,
                confidence=confidence,
                tools_used=[f"routed_to_{agent_type}"],
                metadata={
                    'routed_to': agent_type,
                    'routing_confidence': confidence,
                    'personalized': bool(personal_data),
                    **response.metadata
                }
            )
            
        except Exception as e:
            logger.error("Supervisor processing failed", error=str(e))
            return AgentResponse(
                content=f"I apologize, but I encountered an error processing your request. Please try again or rephrase your question.",
                agent_name="Supervisor",
                agent_type="supervisor",
                confidence=0.0,
                tools_used=[],
                metadata={'error': str(e)}
            )
