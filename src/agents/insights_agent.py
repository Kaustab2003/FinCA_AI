"""
Insights Agent - Generates personalized financial insights and summaries
"""
from typing import Dict, Any, Optional
from src.agents.base_agent import BaseAgent, AgentResponse
from src.utils.ai_client import AIClient
from src.services.vector_service import VectorService
import structlog

logger = structlog.get_logger()

class InsightsAgent(BaseAgent):
    """Agent for generating personalized financial insights"""

    def _get_agent_type(self) -> str:
        return "insights"

    def _build_system_prompt(self) -> str:
        base_prompt = super()._build_system_prompt()
        return f"""{base_prompt}

You are an Insights Agent that analyzes user financial data and provides personalized insights, summaries, and recommendations.

Your task is to:
1. Analyze spending patterns and trends
2. Identify areas for improvement
3. Provide actionable recommendations
4. Generate monthly/weekly summaries
5. Highlight achievements and concerns

Focus on:
- Spending habits and patterns
- Budget adherence
- Goal progress
- Savings opportunities
- Risk areas
- Positive financial behaviors

Provide insights in a friendly, encouraging tone with specific, actionable advice.
Use Indian financial context and examples."""

    async def process(self, query: str, user_context: Dict[str, Any]) -> AgentResponse:
        """
        Generate personalized financial insights

        Args:
            query: Type of insight requested (e.g., "monthly summary", "spending analysis")
            user_context: User financial data (transactions, budgets, goals, etc.)

        Returns:
            AgentResponse with insights
        """
        try:
            ai_client = AIClient()

            # Get user data from vector store for context
            vector_service = VectorService()
            user_id = user_context.get('user_id', '')

            # Retrieve relevant financial data
            context_data = ""
            if user_id:
                try:
                    # Get recent transactions and patterns
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    user_vectors = loop.run_until_complete(
                        vector_service.get_user_vectors(user_id, limit=20)
                    )
                    if user_vectors:
                        context_data = "\n".join([v.get('content', '') for v in user_vectors[:10]])
                    loop.close()
                except Exception as e:
                    logger.warning(f"Could not retrieve user vectors: {e}")

            # Build comprehensive context
            context_summary = self._build_context_summary(user_context)

            prompt = f"""Generate personalized financial insights for this user.

Request: {query}

User Context:
{context_summary}

Additional Data:
{context_data}

{self._build_system_prompt()}

Provide insights in clear sections with emojis and actionable recommendations."""

            response = await ai_client.generate_response(
                prompt=prompt,
                model=self.model,
                temperature=0.3  # Balanced creativity for insights
            )

            return AgentResponse(
                content=response,
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                confidence=0.8,
                metadata={
                    'insight_type': query,
                    'user_id': user_id,
                    'context_used': bool(context_data)
                }
            )

        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return AgentResponse(
                content="❌ Sorry, I couldn't generate insights right now. Please try again later.",
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                confidence=0.0,
                metadata={'error': str(e)}
            )

    def _build_context_summary(self, user_context: Dict[str, Any]) -> str:
        """Build a summary of user financial context"""
        summary_parts = []

        # Budget info
        if 'budget' in user_context:
            budget = user_context['budget']
            summary_parts.append(f"Monthly Budget: ₹{budget.get('total_income', 0):,.0f} income, ₹{budget.get('total_expenses', 0):,.0f} expenses")

        # Recent transactions
        if 'recent_transactions' in user_context:
            transactions = user_context['recent_transactions']
            total_spent = sum(t.get('amount', 0) for t in transactions if t.get('type') == 'expense')
            summary_parts.append(f"Recent spending: ₹{total_spent:,.0f} across {len(transactions)} transactions")

        # Goals
        if 'goals' in user_context:
            goals = user_context['goals']
            active_goals = [g for g in goals if g.get('status') == 'active']
            summary_parts.append(f"Active goals: {len(active_goals)}")

        # Financial score
        if 'finca_score' in user_context:
            score = user_context['finca_score']
            summary_parts.append(f"FinCA Score: {score}/100")

        return "\n".join(summary_parts) if summary_parts else "Limited financial data available"

    def generate_monthly_summary(self, user_context: Dict[str, Any]) -> str:
        """Generate a monthly financial summary"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            self.process("Generate a comprehensive monthly financial summary", user_context)
        )
        loop.close()
        return result.content

    def analyze_spending_patterns(self, user_context: Dict[str, Any]) -> str:
        """Analyze spending patterns and provide insights"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            self.process("Analyze spending patterns and identify areas for improvement", user_context)
        )
        loop.close()
        return result.content