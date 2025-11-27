"""
Budget Service - Handle budget operations
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.config.database import DatabaseClient
from src.services.vector_service import VectorService
from src.utils.logger import logger


class BudgetService:
    """Service for budget operations"""
    
    def __init__(self):
        self.db = DatabaseClient.get_client()
        self.vector_service = VectorService()
    
    async def create_budget(self, user_id: str, budget_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new budget entry"""
        try:
            data = {
                'user_id': user_id,
                'month': budget_data.get('month', datetime.now().strftime('%Y-%m')),
                'income': budget_data.get('income', 0),
                'fixed_expenses': budget_data.get('fixed_expenses', 0),
                'variable_expenses': budget_data.get('variable_expenses', 0),
                'savings': budget_data.get('savings', 0),
                'investments': budget_data.get('investments', 0),
                'fixed_expenses_breakdown': budget_data.get('fixed_expenses_breakdown', {}),
                'variable_expenses_breakdown': budget_data.get('variable_expenses_breakdown', {}),
                'allocations': budget_data.get('allocations', {}),
                'notes': budget_data.get('notes', '')
            }
            
            result = self.db.table('budgets').insert(data).execute()
            
            # Embed budget data for personalized AI
            budget_content = f"""
            Monthly Budget for {data['month']}: 
            Income: ₹{data['income']}, 
            Fixed Expenses: ₹{data['fixed_expenses']}, 
            Variable Expenses: ₹{data['variable_expenses']}, 
            Savings: ₹{data['savings']}, 
            Investments: ₹{data['investments']}
            """
            
            await self.vector_service.embed_user_data(
                user_id=user_id,
                data_type='budget',
                content=budget_content,
                metadata={
                    'month': data['month'],
                    'income': data['income'],
                    'savings': data['savings'],
                    'savings_rate': data['savings']/data['income'] if data['income'] > 0 else 0,
                    'budget_id': result.data[0]['id'] if result.data else None
                }
            )
            
            logger.info("Budget created and embedded", user_id=user_id, month=data['month'])
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error("Budget creation failed", error=str(e), user_id=user_id)
            raise
    
    async def get_budget(self, user_id: str, month: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get budget for a specific month or current month"""
        try:
            if not month:
                month = datetime.now().strftime('%Y-%m')
            
            result = self.db.table('budgets')\
                .select('*')\
                .eq('user_id', user_id)\
                .eq('month', month)\
                .execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error("Budget fetch failed", error=str(e), user_id=user_id)
            return None
    
    async def get_all_budgets(self, user_id: str, limit: int = 12) -> List[Dict[str, Any]]:
        """Get all budgets for a user"""
        try:
            result = self.db.table('budgets')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('month', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error("Budgets fetch failed", error=str(e), user_id=user_id)
            return []
    
    async def update_budget(self, budget_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing budget"""
        try:
            updates['updated_at'] = datetime.now().isoformat()
            
            result = self.db.table('budgets')\
                .update(updates)\
                .eq('id', budget_id)\
                .execute()
            
            logger.info("Budget updated", budget_id=budget_id)
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error("Budget update failed", error=str(e), budget_id=budget_id)
            raise
    
    async def delete_budget(self, budget_id: str) -> bool:
        """Delete a budget"""
        try:
            self.db.table('budgets').delete().eq('id', budget_id).execute()
            logger.info("Budget deleted", budget_id=budget_id)
            return True
            
        except Exception as e:
            logger.error("Budget deletion failed", error=str(e), budget_id=budget_id)
            return False
    
    def calculate_budget_summary(self, budget: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate budget summary metrics"""
        income = budget.get('income', 0)
        fixed = budget.get('fixed_expenses', 0)
        variable = budget.get('variable_expenses', 0)
        savings = budget.get('savings', 0)
        investments = budget.get('investments', 0)
        
        total_expenses = fixed + variable
        total_savings = savings + investments
        balance = income - total_expenses - total_savings
        
        savings_rate = (total_savings / income * 100) if income > 0 else 0
        expense_ratio = (total_expenses / income * 100) if income > 0 else 0
        
        return {
            'total_income': income,
            'total_expenses': total_expenses,
            'total_savings': total_savings,
            'balance': balance,
            'savings_rate': round(savings_rate, 2),
            'expense_ratio': round(expense_ratio, 2),
            'is_balanced': balance >= 0
        }
