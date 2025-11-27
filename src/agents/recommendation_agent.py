"""
Recommendation Agent - Suggests financial goals and adjustments
"""
from typing import Dict, Any, Optional
from src.agents.base_agent import BaseAgent, AgentResponse
from src.utils.ai_client import AIClient
from src.services.vector_service import VectorService
import structlog

logger = structlog.get_logger()

class RecommendationAgent(BaseAgent):
    """Agent for suggesting financial goals and adjustments"""

    def _get_agent_type(self) -> str:
        return "recommendation"

    def _build_system_prompt(self) -> str:
        base_prompt = super()._build_system_prompt()
        return f"""{base_prompt}

You are a Recommendation Agent that suggests personalized financial goals and adjustments based on user data.

Your task is to:
1. Analyze user's current financial situation
2. Suggest new goals based on age, income, and lifestyle
3. Recommend adjustments to existing goals
4. Provide realistic timelines and amounts
5. Consider Indian financial context and priorities

Common goal categories:
- Emergency Fund (3-6 months expenses)
- Home Down Payment
- Vehicle Purchase
- Education/Children's Future
- Retirement Planning
- Debt Reduction
- Investment Growth
- Vacation/Travel Fund
- Wedding/Major Life Events
- Business/Entrepreneurship

Consider factors:
- Age and life stage
- Income stability
- Current savings rate
- Existing debts
- Risk tolerance
- Family situation

Provide specific, achievable recommendations with clear benefits."""

    async def process(self, query: str, user_context: Dict[str, Any]) -> AgentResponse:
        """
        Generate goal recommendations

        Args:
            query: Type of recommendation requested
            user_context: User financial data

        Returns:
            AgentResponse with recommendations
        """
        try:
            ai_client = AIClient()

            # Build comprehensive user profile
            user_profile = self._build_user_profile(user_context)

            prompt = f"""Based on this user's financial profile, provide personalized goal recommendations.

Request: {query}

User Profile:
{user_profile}

{self._build_system_prompt()}

Provide 3-5 specific goal recommendations with:
- Goal name and target amount
- Recommended monthly contribution
- Timeframe
- Expected benefits
- Feasibility assessment

Format as clear, actionable recommendations."""

            response = await ai_client.generate_response(
                prompt=prompt,
                model=self.model,
                temperature=0.4  # Moderate creativity for recommendations
            )

            return AgentResponse(
                content=response,
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                confidence=0.8,
                metadata={
                    'recommendation_type': query,
                    'user_profile_summary': user_profile[:200] + "..." if len(user_profile) > 200 else user_profile
                }
            )

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return AgentResponse(
                content="❌ Sorry, I couldn't generate recommendations right now. Please try again later.",
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                confidence=0.0,
                metadata={'error': str(e)}
            )

    def _build_user_profile(self, user_context: Dict[str, Any]) -> str:
        """Build a comprehensive user profile for recommendations"""
        profile_parts = []

        # Basic info
        age = user_context.get('age', 'unknown')
        income = user_context.get('monthly_income', 0)
        profile_parts.append(f"Age: {age}, Monthly Income: ₹{income:,.0f}")

        # Financial situation
        savings_rate = user_context.get('savings_rate', 0)
        emergency_fund = user_context.get('emergency_fund_months', 0)
        profile_parts.append(f"Savings Rate: {savings_rate:.1f}%, Emergency Fund: {emergency_fund:.1f} months")

        # Current goals
        goals = user_context.get('goals', [])
        if goals:
            active_goals = [g for g in goals if g.get('status') == 'active']
            total_goal_savings = sum(g.get('current_amount', 0) for g in active_goals)
            profile_parts.append(f"Active Goals: {len(active_goals)}, Total Saved: ₹{total_goal_savings:,.0f}")
        else:
            profile_parts.append("No active financial goals")

        # Spending patterns
        monthly_expenses = user_context.get('monthly_expenses', 0)
        if monthly_expenses > 0:
            profile_parts.append(f"Monthly Expenses: ₹{monthly_expenses:,.0f}")

        # Risk profile and preferences
        risk_profile = user_context.get('risk_profile', 'moderate')
        profile_parts.append(f"Risk Profile: {risk_profile}")

        # Life stage indicators
        has_dependents = user_context.get('has_dependents', False)
        marital_status = user_context.get('marital_status', 'single')
        profile_parts.append(f"Marital Status: {marital_status}, Has Dependents: {has_dependents}")

        return "\n".join(profile_parts)

    def suggest_new_goals(self, user_context: Dict[str, Any]) -> str:
        """Suggest new financial goals"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            self.process("Suggest 3-5 new financial goals based on user's profile and life stage", user_context)
        )
        loop.close()
        return result.content

    def adjust_existing_goals(self, user_context: Dict[str, Any]) -> str:
        """Recommend adjustments to existing goals"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            self.process("Review existing goals and suggest adjustments for better achievement", user_context)
        )
        loop.close()
        return result.content