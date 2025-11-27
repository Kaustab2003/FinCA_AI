"""
Conversational Data Entry Agent - Parse natural language to create financial data
"""
from typing import Dict, Any, Optional
from datetime import datetime, date
from src.agents.base_agent import BaseAgent, AgentResponse
from src.services.transaction_service import TransactionService
from src.services.budget_service import BudgetService
from src.services.goals_service import GoalsService
from src.utils.ai_client import AIClient
from src.utils.logger import logger


class ConversationalDataEntryAgent(BaseAgent):
    """Agent for parsing natural language financial data entry"""

    def __init__(self):
        super().__init__()
        self.transaction_service = TransactionService()
        self.budget_service = BudgetService()
        self.goals_service = GoalsService()

    def _get_agent_type(self) -> str:
        return "data_entry"

    async def process(self, query: str, user_context: Dict[str, Any]) -> AgentResponse:
        """Parse natural language and create appropriate financial data"""
        try:
            # Create prompt for data entry parsing
            prompt = f"""
            You are a financial data entry assistant. Parse the user's natural language message and extract structured financial data.

            User Message: "{query}"

            User Context:
            - Current Date: {datetime.now().strftime('%Y-%m-%d')}
            - User ID: {user_context.get('user_id', 'unknown')}

            Analyze the message and determine what type of financial data the user wants to create:
            1. Transaction (income, expense, transfer)
            2. Budget (monthly budget planning)
            3. Goal (financial goal setting)

            For each type, extract the relevant fields:

            TRANSACTION:
            - type: "income", "expense", or "transfer"
            - amount: numeric value (required)
            - category: appropriate category (food, transportation, entertainment, salary, etc.)
            - subcategory: more specific category if mentioned
            - description: brief description of the transaction
            - date: date in YYYY-MM-DD format (default to today if not specified)
            - is_recurring: true/false if mentioned as recurring
            - tags: array of relevant tags

            BUDGET:
            - month: YYYY-MM format (default to current month)
            - income: monthly income amount
            - fixed_expenses: fixed monthly expenses
            - variable_expenses: variable monthly expenses
            - savings: savings amount
            - investments: investment amount
            - fixed_expenses_breakdown: object with category breakdowns
            - variable_expenses_breakdown: object with category breakdowns
            - notes: additional notes

            GOAL:
            - goal_name: name of the goal
            - target_amount: target amount to save/reach
            - current_amount: current saved amount (default 0)
            - target_date: target date in YYYY-MM-DD format
            - category: goal category (emergency_fund, vacation, car, house, etc.)
            - priority: "low", "medium", "high"
            - notes: additional notes

            Return a JSON response with:
            {{
                "intent": "transaction|budget|goal|unknown",
                "confidence": 0.0-1.0,
                "data": {{extracted fields based on intent}},
                "explanation": "brief explanation of what was parsed"
            }}

            If confidence is below 0.7, set intent to "unknown" and ask for clarification.
            """

            # Get LLM response
            ai_client = AIClient()
            response = await ai_client.generate_response(
                prompt=prompt,
                model="deepseek-chat",
                temperature=0.1,  # Low temperature for structured parsing
                max_tokens=1000
            )

            # Parse JSON response
            parsed_data = self._parse_json_response(response)

            if not parsed_data or parsed_data.get('intent') == 'unknown':
                return AgentResponse(
                    content="I'm not sure what financial data you want to add. Could you please be more specific? For example:\n• 'I spent 500 rupees on groceries yesterday'\n• 'I want to save 10000 rupees for a vacation'\n• 'My monthly income is 50000 rupees'",
                    agent_name='Conversational Data Entry Agent',
                    agent_type='data_entry',
                    confidence=parsed_data.get('confidence', 0.0) if parsed_data else 0.0
                )

            # Create the appropriate data based on parsed intent
            user_id = user_context.get('user_id')
            if not user_id:
                raise ValueError("User ID is required for data entry")
            
            result = await self._create_financial_data(
                intent=parsed_data['intent'],
                data=parsed_data['data'],
                user_id=user_id
            )

            return AgentResponse(
                content=result['message'],
                agent_name='Conversational Data Entry Agent',
                agent_type='data_entry',
                confidence=parsed_data['confidence']
            )

        except Exception as e:
            logger.error("Conversational data entry failed", error=str(e))
            return AgentResponse(
                content="I encountered an error while processing your request. Please try again.",
                agent_name='Conversational Data Entry Agent',
                agent_type='data_entry',
                confidence=0.0
            )

    async def _create_financial_data(self, intent: str, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Create the appropriate financial data based on parsed intent"""
        try:
            if intent == 'transaction':
                result = await self.transaction_service.create_transaction(user_id, data)
                return {
                    'success': True,
                    'message': f"✅ Transaction recorded: {data.get('description', 'Transaction')} for ₹{data.get('amount', 0)}",
                    'id': result.get('transaction_id')
                }

            elif intent == 'budget':
                result = await self.budget_service.create_budget(user_id, data)
                month = data.get('month', datetime.now().strftime('%Y-%m'))
                return {
                    'success': True,
                    'message': f"✅ Budget created for {month} with income ₹{data.get('income', 0)}",
                    'id': result.get('budget_id')
                }

            elif intent == 'goal':
                result = await self.goals_service.create_goal(user_id, data)
                return {
                    'success': True,
                    'message': f"✅ Goal created: {data.get('goal_name', 'Goal')} targeting ₹{data.get('target_amount', 0)}",
                    'id': result.get('goal_id')
                }

            else:
                return {
                    'success': False,
                    'message': "Unknown data type"
                }

        except Exception as e:
            logger.error(f"Failed to create {intent} data", error=str(e))
            return {
                'success': False,
                'message': f"Failed to create {intent}: {str(e)}"
            }

    def _parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse JSON response from LLM, with fallback parsing"""
        import json
        import re

        try:
            # Try direct JSON parsing first
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback: extract JSON from markdown code blocks
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass

            # Another fallback: find JSON-like structure
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass

            logger.warning("Failed to parse JSON response", response=response[:200])
            return None