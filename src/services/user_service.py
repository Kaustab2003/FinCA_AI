"""
User Service - Handle user profile operations
"""
from typing import Dict, Any, Optional
from datetime import datetime
from src.config.database import DatabaseClient
from src.utils.encryption import get_encryption
from src.utils.logger import logger


class UserService:
    """Service for user operations"""
    
    def __init__(self):
        self.db = DatabaseClient.get_client()
        self.encryption = get_encryption()
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user profile"""
        try:
            # Encrypt sensitive data
            salary = user_data.get('monthly_income', 0)
            encrypted_salary = self.encryption.encrypt_salary(salary) if salary > 0 else None
            
            data = {
                'email': user_data.get('email'),
                'full_name': user_data.get('full_name'),
                'age': user_data.get('age', 25),
                'city': user_data.get('city', ''),
                'monthly_income': user_data.get('monthly_income', 0),
                'salary_encrypted': encrypted_salary,
                'risk_profile': user_data.get('risk_profile', 'moderate'),
                'language': user_data.get('language', 'en'),
                'currency': user_data.get('currency', 'INR'),
                'onboarding_completed': False
            }
            
            result = self.db.table('user_profiles').insert(data).execute()
            
            logger.info("User created", email=data['email'])
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error("User creation failed", error=str(e))
            raise
    
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile"""
        try:
            result = self.db.table('user_profiles')\
                .select('*')\
                .eq('user_id', user_id)\
                .execute()
            
            if result.data:
                user = result.data[0]
                # Decrypt salary
                if user.get('salary_encrypted'):
                    user['monthly_income'] = self.encryption.decrypt_salary(user['salary_encrypted'])
                return user
            return None
            
        except Exception as e:
            logger.error("User fetch failed", error=str(e), user_id=user_id)
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            result = self.db.table('user_profiles')\
                .select('*')\
                .eq('email', email)\
                .execute()
            
            if result.data:
                user = result.data[0]
                # Decrypt salary
                if user.get('salary_encrypted'):
                    user['monthly_income'] = self.encryption.decrypt_salary(user['salary_encrypted'])
                return user
            return None
            
        except Exception as e:
            logger.error("User fetch by email failed", error=str(e))
            return None
    
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        try:
            # Encrypt salary if being updated
            if 'monthly_income' in updates and updates['monthly_income']:
                updates['salary_encrypted'] = self.encryption.encrypt_salary(updates['monthly_income'])
            
            updates['updated_at'] = datetime.now().isoformat()
            
            result = self.db.table('user_profiles')\
                .update(updates)\
                .eq('user_id', user_id)\
                .execute()
            
            logger.info("User updated", user_id=user_id)
            
            if result.data:
                user = result.data[0]
                # Decrypt salary for return
                if user.get('salary_encrypted'):
                    user['monthly_income'] = self.encryption.decrypt_salary(user['salary_encrypted'])
                return user
            return None
            
        except Exception as e:
            logger.error("User update failed", error=str(e), user_id=user_id)
            raise
    
    async def complete_onboarding(self, user_id: str) -> bool:
        """Mark user onboarding as complete"""
        try:
            await self.update_user(user_id, {'onboarding_completed': True})
            logger.info("Onboarding completed", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Onboarding completion failed", error=str(e), user_id=user_id)
            return False
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user profile (soft delete)"""
        try:
            # In production, implement soft delete by setting deleted_at
            updates = {
                'deleted_at': datetime.now().isoformat(),
                'email': f"deleted_{user_id}@deleted.com"  # Anonymize
            }
            await self.update_user(user_id, updates)
            
            logger.info("User deleted", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("User deletion failed", error=str(e), user_id=user_id)
            return False
