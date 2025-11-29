"""
Transaction Service - Handle transaction operations with vector embedding
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from supabase import create_client, Client
from src.config.settings import settings
from src.utils.session_manager import SessionManager
from src.services.vector_service import VectorService
from src.utils.logger import logger


class TransactionService:
    """Service for transaction operations with vector embedding"""

    def __init__(self):
        # Create authenticated client using session tokens
        access_token = SessionManager.get_access_token()
        refresh_token = SessionManager.get_refresh_token()

        if access_token:
            self.db: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
            try:
                self.db.auth.set_session(access_token, refresh_token)
                logger.info("TransactionService authenticated successfully")
            except Exception as e:
                logger.error(f"Failed to authenticate TransactionService: {e}")
                # Fallback to anonymous client
                self.db = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
        else:
            logger.warning("No access token available for TransactionService, using anonymous client")
            self.db: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
        
        self.vector_service = VectorService()

    async def create_transaction(self, user_id: str, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new transaction and embed it for personalized context"""
        try:
            # Validate required fields
            required_fields = ['date', 'amount', 'type', 'category', 'description']
            for field in required_fields:
                if field not in transaction_data:
                    raise ValueError(f"Missing required field: {field}")

            # Prepare transaction data
            transaction = {
                'user_id': user_id,
                'date': transaction_data['date'],
                'amount': transaction_data['amount'],
                'type': transaction_data['type'],
                'category': transaction_data['category'],
                'subcategory': transaction_data.get('subcategory'),
                'description': transaction_data['description'],
                'source': transaction_data.get('source', 'manual'),
                'is_recurring': transaction_data.get('is_recurring', False),
                'tags': transaction_data.get('tags', [])
            }

            # Insert transaction
            result = self.db.table('transactions').insert(transaction).execute()

            if not result.data:
                raise Exception("Failed to create transaction")

            transaction_id = result.data[0]['id']
            logger.info("Transaction created", transaction_id=transaction_id, user_id=user_id)

            # Embed transaction data for personalized context
            await self._embed_transaction_data(user_id, transaction_data, transaction_id)

            return {
                'success': True,
                'transaction_id': transaction_id,
                'message': 'Transaction created successfully'
            }

        except Exception as e:
            logger.error("Transaction creation failed", error=str(e), user_id=user_id)
            raise

    async def get_transactions(self, user_id: str, limit: int = 50, offset: int = 0,
                             start_date: Optional[date] = None, end_date: Optional[date] = None,
                             category: Optional[str] = None, transaction_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user transactions with optional filtering"""
        try:
            query = self.db.table('transactions').select('*').eq('user_id', user_id)

            if start_date:
                query = query.gte('date', start_date.isoformat())
            if end_date:
                query = query.lte('date', end_date.isoformat())
            if category:
                query = query.eq('category', category)
            if transaction_type:
                query = query.eq('type', transaction_type)

            result = query.order('date', desc=True).range(offset, offset + limit - 1).execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error("Transaction fetch failed", error=str(e), user_id=user_id)
            return []

    async def update_transaction(self, user_id: str, transaction_id: int, update_data: Dict[str, Any]) -> bool:
        """Update transaction and re-embed if content changed"""
        try:
            # Update transaction
            result = self.db.table('transactions').update(update_data).eq('id', transaction_id).eq('user_id', user_id).execute()

            if not result.data:
                return False

            # Re-embed if description or category changed
            if 'description' in update_data or 'category' in update_data or 'amount' in update_data:
                transaction = result.data[0]
                await self._embed_transaction_data(user_id, transaction, transaction_id)

            logger.info("Transaction updated", transaction_id=transaction_id, user_id=user_id)
            return True

        except Exception as e:
            logger.error("Transaction update failed", error=str(e), transaction_id=transaction_id, user_id=user_id)
            return False

    async def delete_transaction(self, user_id: str, transaction_id: int) -> bool:
        """Delete transaction and clean up vector data"""
        try:
            # Get transaction before deletion for cleanup
            result = self.db.table('transactions').select('*').eq('id', transaction_id).eq('user_id', user_id).execute()

            if not result.data:
                return False

            transaction = result.data[0]

            # Delete transaction
            self.db.table('transactions').delete().eq('id', transaction_id).eq('user_id', user_id).execute()

            # Clean up vector data (optional - ChromaDB handles this automatically)
            # We could implement selective cleanup here if needed

            logger.info("Transaction deleted", transaction_id=transaction_id, user_id=user_id)
            return True

        except Exception as e:
            logger.error("Transaction deletion failed", error=str(e), transaction_id=transaction_id, user_id=user_id)
            return False

    async def get_transaction_summary(self, user_id: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]:
        """Get transaction summary statistics"""
        try:
            transactions = await self.get_transactions(user_id, limit=1000, start_date=start_date, end_date=end_date)

            total_income = sum(t['amount'] for t in transactions if t['type'] in ['income', 'credit'])
            total_expenses = sum(t['amount'] for t in transactions if t['type'] in ['expense', 'debit'])
            net_amount = total_income - total_expenses

            # Category breakdown
            category_totals = {}
            for transaction in transactions:
                if transaction['type'] in ['expense', 'debit']:
                    category = transaction['category']
                    category_totals[category] = category_totals.get(category, 0) + transaction['amount']

            return {
                'total_transactions': len(transactions),
                'total_income': total_income,
                'total_expenses': total_expenses,
                'net_amount': net_amount,
                'category_breakdown': category_totals,
                'period': f"{start_date} to {end_date}" if start_date and end_date else "all time"
            }

        except Exception as e:
            logger.error("Transaction summary failed", error=str(e), user_id=user_id)
            return {}

    async def categorize_expense(self, user_id: str, description: str) -> Dict[str, Any]:
        """Auto-categorize an expense using LLM"""
        try:
            from src.agents.expense_categorization_agent import ExpenseCategorizationAgent

            agent = ExpenseCategorizationAgent()
            result = await agent.process(description, {'user_id': user_id})

            return {
                'category': result.metadata.get('category', 'Other'),
                'subcategory': result.metadata.get('subcategory', ''),
                'confidence': result.confidence,
                'reasoning': result.metadata.get('reasoning', ''),
                'agent_response': result
            }

        except Exception as e:
            logger.error("Expense categorization failed", error=str(e), user_id=user_id)
            return {
                'category': 'Other',
                'subcategory': '',
                'confidence': 0.0,
                'reasoning': 'Categorization service unavailable',
                'error': str(e)
            }

    def categorize_expense_sync(self, user_id: str, description: str) -> Dict[str, Any]:
        """Synchronous version of expense categorization"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.categorize_expense(user_id, description))
        loop.close()
        return result

    async def _embed_transaction_data(self, user_id: str, transaction_data: Dict[str, Any], transaction_id: int) -> None:
        """Embed transaction data for personalized LLM context"""
        try:
            # Create meaningful content for embedding
            amount = transaction_data['amount']
            transaction_type = transaction_data['type']
            category = transaction_data['category']
            description = transaction_data['description']
            date_str = transaction_data['date']

            # Format transaction content for embedding
            if transaction_type in ['income', 'credit']:
                content = f"Income transaction: {description} - Amount: ₹{amount} in category {category} on {date_str}"
            elif transaction_type in ['expense', 'debit']:
                content = f"Expense transaction: {description} - Amount: ₹{amount} in category {category} on {date_str}"
            elif transaction_type == 'investment':
                content = f"Investment transaction: {description} - Amount: ₹{amount} in category {category} on {date_str}"
            else:
                content = f"Transaction: {description} - Amount: ₹{amount}, Type: {transaction_type}, Category: {category} on {date_str}"

            # Embed the transaction
            await self.vector_service.embed_user_data(
                user_id=user_id,
                data_type='transaction',
                content=content,
                metadata={
                    'transaction_id': transaction_id,
                    'amount': amount,
                    'type': transaction_type,
                    'category': category,
                    'date': date_str,
                    'description': description
                }
            )

            logger.info("Transaction embedded for user context", user_id=user_id, transaction_id=transaction_id)

        except Exception as e:
            logger.error("Transaction embedding failed", error=str(e), user_id=user_id, transaction_id=transaction_id)
            # Don't raise exception - transaction creation should succeed even if embedding fails