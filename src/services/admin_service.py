"""
Admin Service for FinCA AI
Provides administrative functions for user management and system oversight
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from src.config.database import DatabaseClient
from src.utils.logger import logger


class AdminService:
    """Service for administrative operations"""
    
    def __init__(self):
        # Use service role client for admin operations (bypasses RLS)
        self.db = DatabaseClient.get_service_client()
        self.regular_db = DatabaseClient.get_authenticated_client()
    
    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Get list of all users
        
        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            
        Returns:
            List of user dictionaries
        """
        try:
            result = (self.db.table('user_profiles')
                .select('*')
                .order('created_at', desc=True)
                .range(offset, offset + limit - 1)
                .execute())
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Failed to get all users: {str(e)}")
            return []
    
    def search_users(self, search_term: str) -> List[Dict]:
        """
        Search users by email, name, or user_id
        
        Args:
            search_term: Search string
            
        Returns:
            List of matching users
        """
        try:
            result = (self.db.table('user_profiles')
                .select('*')
                .or_(f'email.ilike.%{search_term}%,full_name.ilike.%{search_term}%,user_id.ilike.%{search_term}%')
                .execute())
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Failed to search users: {str(e)}")
            return []
    
    def get_user_details(self, user_id: str) -> Optional[Dict]:
        """
        Get comprehensive details for a specific user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with user profile and statistics
        """
        try:
            # Get user profile
            profile_result = (self.db.table('user_profiles')
                .select('*')
                .eq('user_id', user_id)
                .execute())
            
            if not profile_result.data:
                return None
            
            profile = profile_result.data[0]
            
            # Get user statistics
            budgets_count = len(self.db.table('budgets').select('id').eq('user_id', user_id).execute().data or [])
            goals_count = len(self.db.table('goals').select('id').eq('user_id', user_id).execute().data or [])
            transactions_count = len(self.db.table('transactions').select('id').eq('user_id', user_id).execute().data or [])
            
            profile['stats'] = {
                'budgets': budgets_count,
                'goals': goals_count,
                'transactions': transactions_count
            }
            
            return profile
        except Exception as e:
            logger.error(f"Failed to get user details: {str(e)}")
            return None
    
    def block_user(self, user_id: str, admin_id: str) -> tuple[bool, str]:
        """
        Block/deactivate a user
        
        Args:
            user_id: User ID to block
            admin_id: Admin performing the action
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Prevent admin from blocking themselves
            if user_id == admin_id:
                return False, "Cannot block yourself"
            
            result = (self.db.table('user_profiles')
                .update({'is_active': False, 'updated_at': datetime.now().isoformat()})
                .eq('user_id', user_id)
                .execute())
            
            if result.data:
                logger.info(f"User {user_id} blocked by admin {admin_id}")
                return True, "User blocked successfully"
            return False, "Failed to block user"
        except Exception as e:
            logger.error(f"Failed to block user: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def unblock_user(self, user_id: str, admin_id: str) -> tuple[bool, str]:
        """
        Unblock/activate a user
        
        Args:
            user_id: User ID to unblock
            admin_id: Admin performing the action
            
        Returns:
            Tuple of (success, message)
        """
        try:
            result = (self.db.table('user_profiles')
                .update({'is_active': True, 'updated_at': datetime.now().isoformat()})
                .eq('user_id', user_id)
                .execute())
            
            if result.data:
                logger.info(f"User {user_id} unblocked by admin {admin_id}")
                return True, "User unblocked successfully"
            return False, "Failed to unblock user"
        except Exception as e:
            logger.error(f"Failed to unblock user: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def change_user_role(self, user_id: str, new_role: str, admin_id: str) -> tuple[bool, str]:
        """
        Change user role (user/admin)
        
        Args:
            user_id: User ID
            new_role: New role ('user' or 'admin')
            admin_id: Admin performing the action
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if new_role not in ['user', 'admin']:
                return False, "Invalid role. Must be 'user' or 'admin'"
            
            # Prevent admin from demoting themselves
            if user_id == admin_id and new_role != 'admin':
                return False, "Cannot change your own role"
            
            result = (self.db.table('user_profiles')
                .update({'role': new_role, 'updated_at': datetime.now().isoformat()})
                .eq('user_id', user_id)
                .execute())
            
            if result.data:
                logger.info(f"User {user_id} role changed to {new_role} by admin {admin_id}")
                return True, f"User role changed to {new_role}"
            return False, "Failed to change role"
        except Exception as e:
            logger.error(f"Failed to change user role: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def delete_user(self, user_id: str, admin_id: str) -> tuple[bool, str]:
        """
        Delete a user and all their data (GDPR compliance)
        
        Args:
            user_id: User ID to delete
            admin_id: Admin performing the action
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Prevent admin from deleting themselves
            if user_id == admin_id:
                return False, "Cannot delete yourself"
            
            # Delete user data from all tables (cascade)
            tables = ['transactions', 'goals', 'budgets', 'chat_history', 
                     'salary_breakup', 'bill_reminders', 'credit_cards',
                     'investment_comparisons', 'quick_money_moves', 
                     'notifications', 'user_preferences']
            
            for table in tables:
                try:
                    self.db.table(table).delete().eq('user_id', user_id).execute()
                except:
                    pass  # Table might not have data
            
            # Finally delete user profile
            result = self.db.table('user_profiles').delete().eq('user_id', user_id).execute()
            
            if result.data:
                logger.warning(f"User {user_id} deleted by admin {admin_id}")
                return True, "User and all data deleted successfully"
            return False, "Failed to delete user"
        except Exception as e:
            logger.error(f"Failed to delete user: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def get_system_stats(self) -> Dict:
        """
        Get system-wide statistics
        
        Returns:
            Dictionary with system statistics
        """
        try:
            total_users = len(self.db.table('user_profiles').select('id').execute().data or [])
            active_users = len(self.db.table('user_profiles').select('id').eq('is_active', True).execute().data or [])
            total_budgets = len(self.db.table('budgets').select('id').execute().data or [])
            total_goals = len(self.db.table('goals').select('id').execute().data or [])
            total_transactions = len(self.db.table('transactions').select('id').execute().data or [])
            
            # Calculate active users (logged in last 7 days)
            seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
            recently_active = len(self.db.table('user_profiles')
                                  .select('id')
                                  .gte('updated_at', seven_days_ago)
                                  .execute().data or [])
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': total_users - active_users,
                'recently_active': recently_active,
                'total_budgets': total_budgets,
                'total_goals': total_goals,
                'total_transactions': total_transactions,
                'avg_budgets_per_user': round(total_budgets / total_users, 2) if total_users > 0 else 0,
                'avg_goals_per_user': round(total_goals / total_users, 2) if total_users > 0 else 0
            }
        except Exception as e:
            logger.error(f"Failed to get system stats: {str(e)}")
            return {}
    
    def get_user_activity_log(self, user_id: str, limit: int = 50) -> List[Dict]:
        """
        Get activity log for a specific user
        
        Args:
            user_id: User ID
            limit: Number of activities to return
            
        Returns:
            List of activity records
        """
        try:
            # Get recent transactions
            activities = []
            
            transactions = (self.db.table('transactions')
                .select('*')
                .eq('user_id', user_id)
                .order('created_at', desc=True)
                .limit(limit)
                .execute())
            
            for txn in (transactions.data or []):
                activities.append({
                    'type': 'Transaction',
                    'description': txn.get('description', 'Transaction'),
                    'amount': txn.get('amount', 0),
                    'date': txn.get('created_at', '')
                })
            
            return activities
        except Exception as e:
            logger.error(f"Failed to get user activity log: {str(e)}")
            return []
