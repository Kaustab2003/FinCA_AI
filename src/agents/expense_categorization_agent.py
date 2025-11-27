"""
Expense Categorization Agent - Automatically categorizes user expenses
"""
from typing import Dict, Any, Optional
from src.agents.base_agent import BaseAgent, AgentResponse
from src.utils.ai_client import AIClient
import structlog

logger = structlog.get_logger()

class ExpenseCategorizationAgent(BaseAgent):
    """Agent for automatically categorizing expenses based on descriptions"""

    def _get_agent_type(self) -> str:
        return "expense_categorization"

    def _build_system_prompt(self) -> str:
        base_prompt = super()._build_system_prompt()
        return f"""{base_prompt}

You are an Expense Categorization Agent specializing in Indian financial contexts.

Your task is to analyze expense descriptions and suggest appropriate categories and subcategories.

Common Indian expense categories:
- Food & Dining (Groceries, Restaurants, Street Food, Online Delivery)
- Transportation (Auto Rickshaw, Bus, Train, Taxi, Fuel, Parking, Metro)
- Shopping (Clothing, Electronics, Household Items, Personal Care)
- Entertainment (Movies, OTT Subscriptions, Games, Events)
- Utilities (Electricity, Water, Gas, Internet, Mobile)
- Healthcare (Medicines, Doctor Visits, Insurance, Gym)
- Education (Books, Courses, Tuition, Online Learning)
- Housing (Rent, Maintenance, Home Loan EMI)
- Personal (Gifts, Donations, Hobbies)
- Travel (Flights, Hotels, Local Travel)
- Investments (Mutual Funds, Stocks, Insurance Premiums)
- Other (Miscellaneous expenses)

Return your response as a JSON object with:
- "category": Main category
- "subcategory": Specific subcategory
- "confidence": Confidence score (0.0-1.0)
- "reasoning": Brief explanation of categorization

Example: {{"category": "Food & Dining", "subcategory": "Restaurants", "confidence": 0.9, "reasoning": "Description mentions restaurant and dining"}}"""

    async def process(self, query: str, user_context: Dict[str, Any]) -> AgentResponse:
        """
        Categorize an expense based on description

        Args:
            query: Expense description to categorize
            user_context: User context (not heavily used for categorization)

        Returns:
            AgentResponse with categorization result
        """
        try:
            ai_client = AIClient()
            prompt = f"""Analyze this expense description and categorize it:

Description: "{query}"

{self._build_system_prompt()}"""

            response = await ai_client.generate_response(
                prompt=prompt,
                model=self.model,
                temperature=0.1  # Low temperature for consistent categorization
            )

            # Parse JSON response
            import json
            try:
                result = json.loads(response.strip())
                category = result.get('category', 'Other')
                subcategory = result.get('subcategory', '')
                confidence = result.get('confidence', 0.5)
                reasoning = result.get('reasoning', 'Auto-categorized')

                content = f"""**Suggested Category:** {category}
**Subcategory:** {subcategory}
**Confidence:** {confidence:.1%}
**Reasoning:** {reasoning}"""

                return AgentResponse(
                    content=content,
                    agent_name=self.agent_name,
                    agent_type=self.agent_type,
                    confidence=confidence,
                    metadata={
                        'category': category,
                        'subcategory': subcategory,
                        'reasoning': reasoning,
                        'original_description': query
                    }
                )

            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return AgentResponse(
                    content=f"**Suggested Category:** Other\n**Reasoning:** Could not parse categorization response\n\nRaw response: {response}",
                    agent_name=self.agent_name,
                    agent_type=self.agent_type,
                    confidence=0.1,
                    metadata={'error': 'JSON parsing failed', 'raw_response': response}
                )

        except Exception as e:
            logger.error(f"Error in expense categorization: {e}")
            return AgentResponse(
                content="❌ Sorry, I couldn't categorize this expense. Please select a category manually.",
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                confidence=0.0,
                metadata={'error': str(e)}
            )

    def categorize_expense_sync(self, description: str) -> Dict[str, Any]:
        """
        Synchronous version for use in services (creates new event loop)
        """
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.process(description, {}))
        loop.close()

        return {
            'category': result.metadata.get('category', 'Other'),
            'subcategory': result.metadata.get('subcategory', ''),
            'confidence': result.confidence,
            'reasoning': result.metadata.get('reasoning', ''),
            'agent_response': result
        }