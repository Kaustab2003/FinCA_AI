"""
DebtManagerAgent - Loan and debt management advice (Updated with Groq/DeepSeek)
"""
from typing import Dict, Any
from src.agents.base_agent import BaseAgent, AgentResponse
from src.utils.ai_client import AIClient
from src.config.settings import settings
from src.utils.logger import logger


class DebtManagerAgent(BaseAgent):
    """Specialized agent for loan and debt management"""
    
    def __init__(self):
        super().__init__()
        self.ai_client = AIClient()
        
        # Typical interest rates in India
        self.interest_rates = {
            'home_loan': (8.5, 9.5),
            'personal_loan': (10.0, 16.0),
            'car_loan': (8.0, 11.0),
            'education_loan': (7.5, 11.0),
            'credit_card': (36.0, 42.0)
        }
        
        provider_info = self.ai_client.get_provider_info()
        logger.info(f"Initialized DebtManagerAgent with {provider_info['provider']} ({provider_info['model']})")
    
    def _get_agent_type(self) -> str:
        return "debt"
    
    def calculate_emi(self, principal: float, annual_rate: float, tenure_months: int) -> Dict[str, Any]:
        """Calculate EMI using standard formula"""
        monthly_rate = annual_rate / 12 / 100
        
        if monthly_rate == 0:
            emi = principal / tenure_months
        else:
            emi = principal * monthly_rate * (1 + monthly_rate)**tenure_months / ((1 + monthly_rate)**tenure_months - 1)
        
        total_payment = emi * tenure_months
        total_interest = total_payment - principal
        interest_percentage = (total_interest / principal * 100) if principal > 0 else 0
        
        return {
            'principal': principal,
            'annual_rate': annual_rate,
            'tenure_months': tenure_months,
            'tenure_years': tenure_months / 12,
            'emi': emi,
            'total_payment': total_payment,
            'total_interest': total_interest,
            'interest_percentage': interest_percentage
        }
    
    def calculate_debt_to_income(self, total_emi: float, monthly_income: float) -> Dict[str, Any]:
        """Calculate debt-to-income ratio"""
        if monthly_income == 0:
            return {'dti_ratio': 0, 'status': 'invalid', 'recommendation': 'Income data required'}
        
        dti_ratio = (total_emi / monthly_income) * 100
        
        if dti_ratio < 30:
            status = "healthy"
            recommendation = "Your debt level is manageable. Good financial health!"
        elif dti_ratio < 40:
            status = "moderate"
            recommendation = "Consider reducing debt. Avoid taking new loans."
        elif dti_ratio < 50:
            status = "high"
            recommendation = "High debt burden. Focus on debt repayment urgently."
        else:
            status = "critical"
            recommendation = "Critical! Seek debt counseling immediately."
        
        return {
            'total_emi': total_emi,
            'monthly_income': monthly_income,
            'dti_ratio': dti_ratio,
            'status': status,
            'recommendation': recommendation
        }
    
    async def process(self, query: str, user_context: Dict[str, Any]) -> AgentResponse:
        """Process debt-related queries"""
        try:
            # Check if AI is available
            if not self.ai_client.is_available():
                return self._get_fallback_response(query, user_context)
            
            salary = user_context.get('salary', 1200000)
            monthly_income = salary / 12
            
            system_prompt = self._build_system_prompt()
            system_prompt += f"""

You are an expert debt and loan advisor for India.

USER PROFILE:
- Monthly Income: {self._format_currency(monthly_income)}
- Annual Income: {self._format_currency(salary)}
- Safe EMI Limit: {self._format_currency(monthly_income * 0.30)} (30% of income)

LOAN TYPES & INTEREST RATES (India):
1. Home Loan: 8.5-9.5% (20-30 years)
2. Personal Loan: 10-16% (1-5 years)
3. Car Loan: 8-11% (5-7 years)
4. Education Loan: 7.5-11% (10-15 years)
5. Credit Card: 36-42% (Revolving)

EMI AFFORDABILITY GUIDELINES:
- Healthy: < 30% of income
- Moderate: 30-40% of income
- High Risk: 40-50% of income
- Critical: > 50% of income

DEBT MANAGEMENT STRATEGIES:
1. Pay high-interest debts first (credit cards)
2. Consider loan consolidation if multiple debts
3. Negotiate lower interest rates with banks
4. Make prepayments to reduce tenure
5. Build emergency fund before taking new loans

EMI CALCULATION FORMULA:
EMI = P × r × (1 + r)^n / ((1 + r)^n - 1)
where P = principal, r = monthly rate, n = months

Provide personalized debt management advice.
"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            content = self.ai_client.chat_completion(messages, temperature=0.4, max_tokens=1200)
            
            provider_info = self.ai_client.get_provider_info()
            logger.info(f"Debt query processed with {provider_info['provider']}")
            
            return AgentResponse(
                content=content,
                agent_name=f"Debt Manager ({provider_info['provider'].title()})",
                agent_type="debt",
                confidence=0.90,
                tools_used=['emi_calculator', 'dti_calculator', provider_info['model']],
                metadata={
                    'provider': provider_info['provider'],
                    'model': provider_info['model'],
                    'is_free': provider_info['is_free']
                }
            )
            
        except Exception as e:
            logger.error("Debt agent processing failed", error=str(e))
            return self._get_fallback_response(query, user_context)
    
    def _get_fallback_response(self, query: str, user_context: Dict[str, Any]) -> AgentResponse:
        """Provide fallback response when AI is unavailable"""
        salary = user_context.get('salary', 1200000)
        monthly_income = salary / 12
        safe_emi = monthly_income * 0.30
        
        # Sample home loan calculation
        home_loan = self.calculate_emi(5000000, 8.5, 240)  # ₹50L, 8.5%, 20 years
        
        fallback_response = f"""**Home Loan EMI Affordability**

Based on monthly income of ₹{monthly_income:,.0f}:

**Safe EMI Limit:**
- 30% of income: ₹{safe_emi:,.0f}/month
- This leaves 70% for living expenses

**Example Loan Scenarios:**

1. **Conservative (₹{safe_emi * 0.8:,.0f} EMI)**
   - Loan amount: ₹{safe_emi * 0.8 * 240 / 1000:,.0f}L
   - Tenure: 20 years
   - Rate: 8.5%

2. **Moderate (₹{safe_emi:,.0f} EMI)**
   - Loan amount: ₹{safe_emi * 240 / 1000:,.0f}L
   - Tenure: 20 years
   - Rate: 8.5%

3. **Maximum (₹{safe_emi * 1.2:,.0f} EMI)**
   - Loan amount: ₹{safe_emi * 1.2 * 240 / 1000:,.0f}L
   - Tenure: 20 years
   - Rate: 8.5%
   - ⚠️ Risky - 36% of income

**Sample: ₹50L Home Loan @ 8.5%**
- EMI: ₹{home_loan['emi']:,.0f}/month
- Total paid: ₹{home_loan['total_payment']:,.0f}
- Interest: ₹{home_loan['total_interest']:,.0f}

**EMI Management Tips:**
1. Keep total EMIs under 40% of income
2. Build 6-month emergency fund first
3. Consider prepayment to reduce tenure
4. Compare rates across banks
5. Negotiate for lower interest rates

**Debt-to-Income Ratio Guidelines:**
- Healthy: <30% → Financial stability
- Moderate: 30-40% → Manageable risk
- High: 40-50% → Reduce debt urgently
- Critical: >50% → Seek counseling

**Priority Debt Repayment:**
1. Credit cards (36-42%) - Highest priority
2. Personal loans (10-16%)
3. Car loans (8-11%)
4. Home loans (8.5-9.5%) - Tax benefits available

*Using smart fallback mode with real EMI calculations*
"""
        
        return AgentResponse(
            content=fallback_response,
            agent_name="Debt Manager (Fallback)",
            agent_type="debt",
            confidence=0.80,
            tools_used=['fallback_mode', 'emi_calculator', 'dti_calculator'],
            metadata={'fallback': True, 'reason': 'AI provider unavailable'}
        )
