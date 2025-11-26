"""
Chat Service - Handle AI chat operations
"""
from typing import Dict, Any, List
from datetime import datetime
from src.config.database import DatabaseClient
from src.agents.supervisor import SupervisorAgent
from src.utils.logger import logger


class ChatService:
    """Service for AI chat operations"""
    
    def __init__(self):
        self.db = DatabaseClient.get_client()
        self.supervisor = SupervisorAgent()
    
    async def process_message(self, user_id: str, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a chat message and get AI response"""
        try:
            # Skip database saves (table not created yet)
            # await self.save_message(user_id, 'user', message)
            
            # Get AI response from supervisor
            response = await self.supervisor.process(message, user_context)
            
            # Skip database saves (table not created yet)
            # await self.save_message(user_id, 'assistant', response.content, {
            #     'agent_type': response.agent_type,
            #     'agent_name': response.agent_name,
            #     'confidence': response.confidence,
            #     'tools_used': response.tools_used
            # })
            
            logger.info("Chat message processed", 
                       user_id=user_id,
                       agent_type=response.agent_type,
                       confidence=response.confidence)
            
            return {
                'response': response.content,
                'agent_name': response.agent_name,
                'agent_type': response.agent_type,
                'confidence': response.confidence,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Chat processing failed", error=str(e), user_id=user_id)
            return {
                'response': "I'm sorry, I encountered an error. Please try again.",
                'agent_name': 'System',
                'agent_type': 'error',
                'confidence': 0.0,
                'error': str(e)
            }
    
    async def save_message(self, user_id: str, role: str, content: str, metadata: Dict[str, Any] = None):
        """Save a message to chat history"""
        try:
            data = {
                'user_id': user_id,
                'role': role,
                'content': content,
                'metadata': metadata or {}
            }
            
            self.db.table('chat_history').insert(data).execute()
            
        except Exception as e:
            logger.error("Message save failed", error=str(e), user_id=user_id)
    
    async def get_chat_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat history for a user"""
        try:
            result = self.db.table('chat_history')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('created_at', desc=False)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error("Chat history fetch failed", error=str(e), user_id=user_id)
            return []
    
    async def clear_chat_history(self, user_id: str) -> bool:
        """Clear chat history for a user"""
        try:
            self.db.table('chat_history').delete().eq('user_id', user_id).execute()
            logger.info("Chat history cleared", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Chat history clear failed", error=str(e), user_id=user_id)
            return False
