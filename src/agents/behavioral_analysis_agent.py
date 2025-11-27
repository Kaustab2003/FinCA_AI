"""
Behavioral Analysis Agent - Analyzes spending habits and provides behavioral insights
"""
from typing import Dict, Any, Optional
from src.agents.base_agent import BaseAgent, AgentResponse
from src.utils.ai_client import AIClient
from src.services.vector_service import VectorService
import structlog

logger = structlog.get_logger()

class BehavioralAnalysisAgent(BaseAgent):
    """Agent for analyzing spending behavior and habits"""

    def _get_agent_type(self) -> str:
        return "behavioral_analysis"

    def _build_system_prompt(self) -> str:
        base_prompt = super()._build_system_prompt()
        return f"""{base_prompt}

You are a Behavioral Analysis Agent that studies spending patterns and provides psychological insights into financial habits.

Your task is to:
1. Identify spending patterns and triggers
2. Analyze behavioral tendencies (impulse buying, emotional spending, etc.)
3. Provide behavioral nudges and habit-forming suggestions
4. Highlight positive financial behaviors to reinforce
5. Suggest strategies to improve financial discipline

Focus on:
- Spending triggers and patterns
- Time-based analysis (weekdays vs weekends, monthly cycles)
- Category-wise behavioral insights
- Emotional spending indicators
- Habit formation strategies
- Cognitive biases in spending

Use behavioral economics principles and provide actionable, non-judgmental advice.
Frame insights positively and focus on improvement opportunities."""

    async def process(self, query: str, user_context: Dict[str, Any]) -> AgentResponse:
        """
        Analyze user spending behavior

        Args:
            query: Type of analysis requested
            user_context: User transaction data and patterns

        Returns:
            AgentResponse with behavioral insights
        """
        try:
            ai_client = AIClient()

            # Build behavioral context from user data
            behavioral_context = self._build_behavioral_context(user_context)

            prompt = f"""Analyze this user's spending behavior and provide insights.

Analysis Request: {query}

Behavioral Context:
{behavioral_context}

{self._build_system_prompt()}

Provide insights in these sections:
1. **Spending Patterns** - Key patterns and trends
2. **Behavioral Tendencies** - Psychological insights
3. **Positive Habits** - What they're doing right
4. **Improvement Areas** - Areas for growth
5. **Actionable Tips** - Specific, behavioral nudges

Be encouraging and focus on positive reinforcement."""

            response = await ai_client.generate_response(
                prompt=prompt,
                model=self.model,
                temperature=0.3  # Balanced for insightful analysis
            )

            return AgentResponse(
                content=response,
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                confidence=0.8,
                metadata={
                    'analysis_type': query,
                    'behavioral_patterns': behavioral_context[:200] + "..." if len(behavioral_context) > 200 else behavioral_context
                }
            )

        except Exception as e:
            logger.error(f"Error in behavioral analysis: {e}")
            return AgentResponse(
                content="❌ Sorry, I couldn't analyze your spending behavior right now. Please try again later.",
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                confidence=0.0,
                metadata={'error': str(e)}
            )

    def _build_behavioral_context(self, user_context: Dict[str, Any]) -> str:
        """Build behavioral context from user data"""
        context_parts = []

        # Transaction patterns
        transactions = user_context.get('recent_transactions', [])
        if transactions:
            # Category breakdown
            category_spending = {}
            for txn in transactions:
                if txn.get('type') == 'expense':
                    category = txn.get('category', 'Other')
                    amount = txn.get('amount', 0)
                    category_spending[category] = category_spending.get(category, 0) + amount

            if category_spending:
                top_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:3]
                context_parts.append(f"Top spending categories: {', '.join([f'{cat} (₹{amt:,.0f})' for cat, amt in top_categories])}")

            # Time patterns (weekday vs weekend if available)
            weekday_spending = sum(t.get('amount', 0) for t in transactions
                                 if t.get('type') == 'expense' and self._is_weekday(t.get('date', '')))
            weekend_spending = sum(t.get('amount', 0) for t in transactions
                                 if t.get('type') == 'expense' and not self._is_weekday(t.get('date', '')))

            if weekday_spending > 0 or weekend_spending > 0:
                total_spending = weekday_spending + weekend_spending
                if total_spending > 0:
                    weekday_pct = (weekday_spending / total_spending) * 100
                    weekend_pct = (weekend_spending / total_spending) * 100
                    context_parts.append(f"Spending pattern: {weekday_pct:.1f}% weekdays, {weekend_pct:.1f}% weekends")

            # Average transaction size
            expense_txns = [t for t in transactions if t.get('type') == 'expense']
            if expense_txns:
                avg_transaction = sum(t.get('amount', 0) for t in expense_txns) / len(expense_txns)
                context_parts.append(f"Average transaction size: ₹{avg_transaction:,.0f}")

        # Budget adherence
        budget_adherence = user_context.get('budget_adherence', 0)
        if budget_adherence > 0:
            context_parts.append(f"Budget adherence: {budget_adherence:.1f}%")

        # Goal progress
        goals_progress = user_context.get('goals_progress', 0)
        if goals_progress > 0:
            context_parts.append(f"Goal achievement rate: {goals_progress:.1f}%")

        # Financial score components
        behavioral_score = user_context.get('behavioral_score', 0)
        if behavioral_score > 0:
            context_parts.append(f"Behavioral score: {behavioral_score}/100")

        return "\n".join(context_parts) if context_parts else "Limited behavioral data available"

    def _is_weekday(self, date_str: str) -> bool:
        """Check if a date string represents a weekday"""
        try:
            from datetime import datetime
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.weekday() < 5  # Monday-Friday
        except:
            return True  # Default to weekday if parsing fails

    def analyze_spending_behavior(self, user_context: Dict[str, Any]) -> str:
        """Analyze overall spending behavior"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            self.process("Provide a comprehensive analysis of spending behavior and habits", user_context)
        )
        loop.close()
        return result.content

    def identify_spending_triggers(self, user_context: Dict[str, Any]) -> str:
        """Identify potential spending triggers"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            self.process("Identify spending triggers and emotional spending patterns", user_context)
        )
        loop.close()
        return result.content