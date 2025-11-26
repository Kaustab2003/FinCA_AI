"""
InvestmentAdvisorAgent - Portfolio and investment advice (Updated with Groq/DeepSeek)
"""
from typing import Dict, Any
from src.agents.base_agent import BaseAgent, AgentResponse
from src.utils.ai_client import AIClient
from src.config.settings import settings
from src.utils.logger import logger


class InvestmentAdvisorAgent(BaseAgent):
    """Specialized agent for investment advice and portfolio management"""
    
    def __init__(self):
        super().__init__()
        self.ai_client = AIClient()
        
        # Risk-based asset allocation
        self.allocations = {
            'conservative': {'equity': 20, 'debt': 60, 'gold': 10, 'cash': 10},
            'moderate': {'equity': 50, 'debt': 35, 'gold': 10, 'cash': 5},
            'aggressive': {'equity': 75, 'debt': 15, 'gold': 5, 'cash': 5}
        }
        
        provider_info = self.ai_client.get_provider_info()
        logger.info(f"Initialized InvestmentAdvisorAgent with {provider_info['provider']} ({provider_info['model']})")
    
    def _get_agent_type(self) -> str:
        return "investment"
    
    def calculate_sip_returns(self, monthly_amount: float, years: int, expected_return: float = 12) -> Dict[str, Any]:
        """Calculate SIP returns using compound interest formula"""
        months = years * 12
        monthly_rate = expected_return / 12 / 100
        
        # Future value of SIP = P × ((1 + r)^n - 1) / r × (1 + r)
        if monthly_rate > 0:
            fv = monthly_amount * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
        else:
            fv = monthly_amount * months
        
        invested = monthly_amount * months
        returns = fv - invested
        
        return {
            'monthly_investment': monthly_amount,
            'years': years,
            'expected_return': expected_return,
            'total_invested': invested,
            'expected_returns': returns,
            'maturity_value': fv,
            'wealth_gain_percentage': (returns / invested * 100) if invested > 0 else 0
        }
    
    def recommend_allocation(self, risk_profile: str, age: int) -> Dict[str, int]:
        """Recommend asset allocation based on risk profile and age"""
        base_allocation = self.allocations.get(risk_profile, self.allocations['moderate']).copy()
        
        # Age-based adjustment (reduce equity with age)
        if age > 40:
            reduction = min((age - 40) * 2, 20)
            base_allocation['equity'] = max(base_allocation['equity'] - reduction, 20)
            base_allocation['debt'] += reduction
        
        return base_allocation
    
    def _build_investment_context(self, user_context: Dict[str, Any]) -> str:
        """Build context about user's investment profile"""
        salary = user_context.get('salary', 0)
        age = user_context.get('age', 25)
        risk_profile = user_context.get('risk_profile', 'moderate')
        
        context = f"User investment profile:\n"
        context += f"- Age: {age} (Time horizon: {65-age} years to retirement)\n"
        context += f"- Income: {self._format_currency(salary)}\n"
        context += f"- Risk profile: {risk_profile.title()}\n"
        
        allocation = self.recommend_allocation(risk_profile, age)
        context += f"\nRecommended allocation:\n"
        for asset, percentage in allocation.items():
            context += f"- {asset.title()}: {percentage}%\n"
        
        # Sample SIP calculation
        if salary > 0:
            suggested_sip = salary * 0.20 / 12  # 20% of annual income
            sip_result = self.calculate_sip_returns(suggested_sip, 10, 12)
            context += f"\nSample SIP (₹{suggested_sip:,.0f}/month for 10 years):\n"
            context += f"- Total invested: {self._format_currency(sip_result['total_invested'])}\n"
            context += f"- Expected value: {self._format_currency(sip_result['maturity_value'])}\n"
        
        return context
    
    async def process(self, query: str, user_context: Dict[str, Any]) -> AgentResponse:
        """Process investment-related queries"""
        try:
            # Check if AI is available
            if not self.ai_client.is_available():
                return self._get_fallback_response(query, user_context)
            
            system_prompt = self._build_system_prompt()
            system_prompt += f"""

You are an expert investment advisor specializing in the Indian market.

KEY INVESTMENT OPTIONS IN INDIA:
1. Equity:
   - Direct stocks (NSE/BSE)
   - Equity mutual funds (Large/Mid/Small cap)
   - Index funds (Nifty 50, Sensex)
   - ELSS (Tax-saving, 3-year lock-in)

2. Debt:
   - Fixed Deposits (6-7% returns)
   - Debt mutual funds (7-8% returns)
   - PPF (7.1%, 15-year lock-in, tax-free)
   - Government bonds (7-7.5%)

3. Hybrid:
   - Balanced advantage funds
   - Hybrid mutual funds
   - NPS (Pension, tax benefits)

4. Alternative:
   - Gold (Sovereign Gold Bonds, Gold ETFs)
   - REITs (Real estate)
   - Peer-to-peer lending

{self._build_investment_context(user_context)}

IMPORTANT PRINCIPLES:
- Start early, benefit from compounding
- Diversify across asset classes
- SIP > lump sum (rupee cost averaging)
- Review portfolio quarterly
- Emergency fund: 6 months expenses
- Don't time the market

Provide personalized, actionable advice based on user's profile.
"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            content = self.ai_client.chat_completion(messages, temperature=0.5, max_tokens=1200)
            
            provider_info = self.ai_client.get_provider_info()
            logger.info(f"Investment query processed with {provider_info['provider']}")
            
            return AgentResponse(
                content=content,
                agent_name=f"Investment Advisor ({provider_info['provider'].title()})",
                agent_type="investment",
                confidence=0.90,
                tools_used=['sip_calculator', 'allocation_optimizer', provider_info['model']],
                metadata={
                    'provider': provider_info['provider'],
                    'model': provider_info['model'],
                    'is_free': provider_info['is_free']
                }
            )
            
        except Exception as e:
            logger.error("Investment agent processing failed", error=str(e))
            return self._get_fallback_response(query, user_context)
    
    def _get_fallback_response(self, query: str, user_context: Dict[str, Any]) -> AgentResponse:
        """Provide fallback response when AI is unavailable"""
        salary = user_context.get('salary', 600000)
        age = user_context.get('age', 25)
        risk_profile = user_context.get('risk_profile', 'moderate')
        
        allocation = self.recommend_allocation(risk_profile, age)
        suggested_sip = salary * 0.20 / 12
        sip_result = self.calculate_sip_returns(suggested_sip, 10, 12)
        
        fallback_response = f"""**Investment Advice for Your Profile**

Based on your profile (Age: {age}, Income: ₹{salary:,}, Risk: {risk_profile}):

**Recommended Asset Allocation:**
- Equity: {allocation['equity']}%
- Debt: {allocation['debt']}%
- Gold: {allocation['gold']}%
- Cash: {allocation['cash']}%

**Investment Strategy:**

1. **Start SIP Immediately**
   - Suggested amount: ₹{suggested_sip:,.0f}/month (20% of income)
   - Investment horizon: 10 years
   - Expected maturity: ₹{sip_result['maturity_value']:,.0f}
   - Total returns: ₹{sip_result['expected_returns']:,.0f}

2. **Equity Investments ({allocation['equity']}%)**
   - 40%: Nifty 50 Index Fund
   - 30%: Large-cap mutual funds
   - 20%: Mid-cap funds
   - 10%: Small-cap/sector funds

3. **Debt Investments ({allocation['debt']}%)**
   - 50%: PPF (tax-free)
   - 30%: Debt mutual funds
   - 20%: Fixed deposits

4. **Gold ({allocation['gold']}%)**
   - Sovereign Gold Bonds (2.5% interest + price appreciation)

**Key Tips:**
✅ Start today - time in market beats timing market
✅ Automate SIPs on salary day
✅ Increase SIP by 10% yearly
✅ Review portfolio quarterly
✅ Stay invested minimum 5 years
✅ Build 6-month emergency fund first

*Using smart fallback mode with real calculations*
"""
        
        return AgentResponse(
            content=fallback_response,
            agent_name="Investment Advisor (Fallback)",
            agent_type="investment",
            confidence=0.80,
            tools_used=['fallback_mode', 'sip_calculator', 'allocation_optimizer'],
            metadata={'fallback': True, 'reason': 'AI provider unavailable'}
        )
