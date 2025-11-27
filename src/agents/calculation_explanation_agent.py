"""
Calculation Explanation Agent - Provides plain-language explanations for financial calculations
"""
from typing import Dict, Any, Optional
from src.agents.base_agent import BaseAgent, AgentResponse
from src.utils.ai_client import AIClient
from src.services.vector_service import VectorService
import structlog

logger = structlog.get_logger()

class CalculationExplanationAgent(BaseAgent):
    """Agent for explaining financial calculations in plain language"""

    def _get_agent_type(self) -> str:
        return "calculation_explanation"

    def _build_system_prompt(self) -> str:
        base_prompt = super()._build_system_prompt()
        return f"""{base_prompt}

You are a Calculation Explanation Agent that explains financial calculations and formulas in simple, understandable language.

Your task is to:
1. Break down complex financial calculations into simple steps
2. Explain the reasoning behind formulas and assumptions
3. Provide real-world context and examples
4. Highlight what the numbers mean for the user's financial situation
5. Suggest related calculations or considerations

Focus on:
- Tax calculations (income tax, HRA, deductions)
- Investment returns (SIP, lumpsum, CAGR)
- Loan calculations (EMI, interest, prepayment)
- Salary breakup (CTC, take-home, benefits)
- Retirement planning (corpus, inflation, withdrawals)

Use Indian financial context and provide explanations that help users make informed decisions.
Structure explanations with:
- What the calculation does
- Step-by-step breakdown
- Key assumptions and variables
- What the result means
- Related considerations or tips"""

    async def process(self, query: str, user_context: Dict[str, Any]) -> AgentResponse:
        """
        Explain a financial calculation

        Args:
            query: Description of the calculation to explain (e.g., "Explain my HRA exemption calculation")
            user_context: Calculation details and user financial data

        Returns:
            AgentResponse with plain-language explanation
        """
        try:
            # Extract calculation details from context
            calculation_data = user_context.get('calculation_data', {})
            calculation_type = user_context.get('calculation_type', 'general')

            # Build comprehensive context for explanation
            explanation_context = f"""
            Calculation Type: {calculation_type}
            User Details: {user_context.get('user_details', 'Not provided')}
            Calculation Parameters: {calculation_data}
            Result: {user_context.get('result', 'Not provided')}
            """

            # Use AI to generate explanation
            prompt = f"""Please explain this financial calculation in simple, easy-to-understand language:

{query}

Context:
{explanation_context}

Provide a clear, step-by-step explanation that helps the user understand:
1. What this calculation does
2. How it's computed
3. What the result means for their finances
4. Any important assumptions or considerations
5. Related tips or suggestions

Use Indian financial context and examples where relevant."""

            messages = [{"role": "user", "content": prompt}]

            response = self.ai_client.chat_completion(
                messages,
                temperature=0.3,  # Lower temperature for consistent explanations
                max_tokens=800
            )

            content = response.strip()

            return AgentResponse(
                content=content,
                agent_name="Calculation Explainer",
                agent_type="calculation_explanation",
                confidence=0.95,  # High confidence for explanations
                tools_used=["ai_explanation"],
                metadata={
                    'calculation_type': calculation_type,
                    'explanation_length': len(content),
                    'user_context_used': bool(user_context.get('user_details'))
                }
            )

        except Exception as e:
            logger.error("Calculation explanation failed", error=str(e))
            return AgentResponse(
                content="I'm sorry, I couldn't generate an explanation for this calculation. Please try again or provide more details about the calculation you want explained.",
                agent_name="Calculation Explainer",
                agent_type="calculation_explanation",
                confidence=0.0,
                tools_used=[],
                metadata={'error': str(e)}
            )

    def explain_tax_calculation(self, tax_details: Dict[str, Any]) -> str:
        """Provide a focused explanation for tax calculations"""
        try:
            prompt = f"""Explain this tax calculation in simple terms:

Tax Details: {tax_details}

Break down:
1. How the tax amount was calculated
2. Which tax slab applies
3. What deductions were considered
4. What the final take-home means
5. Tax-saving suggestions

Keep it conversational and easy to understand."""

            messages = [{"role": "user", "content": prompt}]
            response = self.ai_client.chat_completion(messages, temperature=0.2, max_tokens=600)

            return response.strip()

        except Exception as e:
            logger.error("Tax explanation failed", error=str(e))
            return "Unable to generate tax calculation explanation."

    def explain_investment_calculation(self, investment_details: Dict[str, Any]) -> str:
        """Provide explanation for investment return calculations"""
        try:
            prompt = f"""Explain this investment calculation clearly:

Investment Details: {investment_details}

Explain:
1. How returns are calculated (SIP vs lumpsum)
2. What CAGR/XIRR means
3. Impact of different time periods
4. Effect of additional contributions
5. Realistic expectations and risks

Use simple language and Indian investment context."""

            messages = [{"role": "user", "content": prompt}]
            response = self.ai_client.chat_completion(messages, temperature=0.2, max_tokens=600)

            return response.strip()

        except Exception as e:
            logger.error("Investment explanation failed", error=str(e))
            return "Unable to generate investment calculation explanation."

    def explain_loan_calculation(self, loan_details: Dict[str, Any]) -> str:
        """Provide explanation for loan EMI calculations"""
        try:
            prompt = f"""Explain this loan calculation in simple terms:

Loan Details: {loan_details}

Break down:
1. How EMI is calculated
2. Interest vs principal components
3. Total interest paid over loan tenure
4. Prepayment benefits and savings
5. What different tenure lengths mean

Make it easy to understand for loan decisions."""

            messages = [{"role": "user", "content": prompt}]
            response = self.ai_client.chat_completion(messages, temperature=0.2, max_tokens=600)

            return response.strip()

        except Exception as e:
            logger.error("Loan explanation failed", error=str(e))
            return "Unable to generate loan calculation explanation."