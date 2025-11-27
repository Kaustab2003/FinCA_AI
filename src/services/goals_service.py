"""
Goals Service - Handle financial goals operations
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.config.database import DatabaseClient
from src.services.vector_service import VectorService
from src.utils.logger import logger


class GoalsService:
    """Service for financial goals operations"""
    
    def __init__(self):
        self.db = DatabaseClient.get_client()
        self.vector_service = VectorService()
    
    async def create_goal(self, user_id: str, goal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new financial goal"""
        try:
            data = {
                'user_id': user_id,
                'goal_name': goal_data.get('goal_name', ''),
                'target_amount': goal_data.get('target_amount', 0),
                'current_amount': goal_data.get('current_amount', 0),
                'target_date': goal_data.get('target_date'),
                'category': goal_data.get('category', 'other'),
                'priority': goal_data.get('priority', 'medium'),
                'notes': goal_data.get('notes', ''),
                'status': 'active'
            }
            
            result = self.db.table('goals').insert(data).execute()
            
            # Embed goal data for personalized AI
            goal_content = f"""
            Financial Goal: {data['goal_name']}
            Target Amount: ₹{data['target_amount']}
            Current Amount: ₹{data['current_amount']}
            Target Date: {data['target_date']}
            Category: {data['category']}
            Priority: {data['priority']}
            Progress: {data['current_amount']/data['target_amount']*100:.1f}% completed
            """
            
            await self.vector_service.embed_user_data(
                user_id=user_id,
                data_type='goal',
                content=goal_content,
                metadata={
                    'goal_name': data['goal_name'],
                    'target_amount': data['target_amount'],
                    'current_amount': data['current_amount'],
                    'progress': data['current_amount']/data['target_amount'] if data['target_amount'] > 0 else 0,
                    'category': data['category'],
                    'priority': data['priority'],
                    'goal_id': result.data[0]['id'] if result.data else None
                }
            )
            
            logger.info("Goal created and embedded", user_id=user_id, goal_name=data['goal_name'])
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error("Goal creation failed", error=str(e), user_id=user_id)
            raise
    
    async def get_goal(self, goal_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific goal"""
        try:
            result = self.db.table('goals')\
                .select('*')\
                .eq('id', goal_id)\
                .execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error("Goal fetch failed", error=str(e), goal_id=goal_id)
            return None
    
    async def get_all_goals(self, user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all goals for a user"""
        try:
            query = self.db.table('goals').select('*').eq('user_id', user_id)
            
            if status:
                query = query.eq('status', status)
            
            result = query.order('created_at', desc=True).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error("Goals fetch failed", error=str(e), user_id=user_id)
            return []
    
    async def update_goal(self, goal_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing goal"""
        try:
            updates['updated_at'] = datetime.now().isoformat()
            
            result = self.db.table('goals')\
                .update(updates)\
                .eq('id', goal_id)\
                .execute()
            
            logger.info("Goal updated", goal_id=goal_id)
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error("Goal update failed", error=str(e), goal_id=goal_id)
            raise
    
    async def delete_goal(self, goal_id: str) -> bool:
        """Delete a goal"""
        try:
            self.db.table('goals').delete().eq('id', goal_id).execute()
            logger.info("Goal deleted", goal_id=goal_id)
            return True
            
        except Exception as e:
            logger.error("Goal deletion failed", error=str(e), goal_id=goal_id)
            return False
    
    async def add_progress(self, goal_id: str, amount: float, note: str = "") -> Dict[str, Any]:
        """Add progress to a goal"""
        try:
            # Get current goal
            goal = await self.get_goal(goal_id)
            if not goal:
                raise ValueError(f"Goal {goal_id} not found")
            
            # Update current amount
            new_amount = goal['current_amount'] + amount
            
            updates = {
                'current_amount': new_amount,
                'updated_at': datetime.now().isoformat()
            }
            
            # Mark as completed if target reached
            if new_amount >= goal['target_amount']:
                updates['status'] = 'completed'
            
            return await self.update_goal(goal_id, updates)
            
        except Exception as e:
            logger.error("Goal progress update failed", error=str(e), goal_id=goal_id)
            raise
    
    def calculate_goal_metrics(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics for a goal"""
        target = goal.get('target_amount', 0)
        current = goal.get('current_amount', 0)
        target_date = goal.get('target_date')
        
        remaining = target - current
        progress = (current / target * 100) if target > 0 else 0
        
        metrics = {
            'progress_percentage': round(progress, 2),
            'amount_remaining': remaining,
            'is_on_track': progress >= 50  # Simple heuristic
        }
        
        # Calculate monthly requirement if target date exists
        if target_date:
            try:
                target_dt = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
                months_left = max((target_dt.year - datetime.now().year) * 12 + 
                                 (target_dt.month - datetime.now().month), 1)
                
                metrics['months_remaining'] = months_left
                metrics['monthly_required'] = remaining / months_left if months_left > 0 else remaining
                
            except Exception as e:
                logger.warning("Could not calculate date metrics", error=str(e))
        
        return metrics
