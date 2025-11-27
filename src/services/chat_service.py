"""
Chat Service - Handle AI chat operations
"""
from typing import Dict, Any, List
from datetime import datetime
from src.config.database import DatabaseClient
from src.agents.supervisor import SupervisorAgent
from src.services.vector_service import VectorService
from src.utils.logger import logger


class ChatService:
    """Service for AI chat operations"""
    
    def __init__(self):
        self.db = DatabaseClient.get_client()
        self.supervisor = SupervisorAgent()
        self.vector_service = VectorService()
    
    async def process_message(self, user_id: str, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a chat message and get AI response"""
        try:
            # Save user message to chat history
            await self.save_message(user_id, 'user', message)
            
            # Get user-specific relevant context from vector store
            user_vectors = await self.vector_service.retrieve_user_context(user_id, message, top_k=5)
            
            # Enhance user context with personal data
            enhanced_context = user_context.copy()
            enhanced_context['user_data'] = user_vectors
            enhanced_context['personal_finances'] = self._format_user_vectors(user_vectors)
            
            # Get AI response from supervisor with enhanced context
            response = await self.supervisor.process(message, enhanced_context)
            
            # Save assistant response to chat history
            await self.save_message(user_id, 'assistant', response.content, {
                'agent_type': response.agent_type,
                'confidence': response.confidence,
                'tool_calls': response.tools_used,
                'user_context_used': len(user_vectors)
            })
            
            logger.info("Chat message processed with user context", 
                       user_id=user_id,
                       agent_type=response.agent_type,
                       user_vectors_used=len(user_vectors))
            
            return {
                'response': response.content,
                'agent_name': response.agent_name,
                'agent_type': response.agent_type,
                'confidence': response.confidence,
                'user_context_used': len(user_vectors),
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
                'message': content,  # Database column is 'message'
                'agent_type': metadata.get('agent_type') if metadata else None,
                'confidence': metadata.get('confidence') if metadata else None,
                'tool_calls': metadata.get('tool_calls') if metadata else None,
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
    
    def _format_user_vectors(self, vectors: List[Dict]) -> str:
        """Format user vectors for LLM context"""
        context_parts = []
        for vector in vectors:
            if vector['data_type'] == 'budget':
                context_parts.append(f"Your budget: {vector['content']}")
            elif vector['data_type'] == 'goal':
                context_parts.append(f"Your goal: {vector['content']}")
            elif vector['data_type'] == 'transaction':
                context_parts.append(f"Your transaction: {vector['content']}")
            else:
                context_parts.append(f"Your data: {vector['content']}")
        
        return "\n".join(context_parts) if context_parts else "No personal financial data available."
    
    async def clear_chat_history(self, user_id: str) -> bool:
        """Clear chat history for a user"""
        try:
            self.db.table('chat_history').delete().eq('user_id', user_id).execute()
            logger.info("Chat history cleared", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Chat history clear failed", error=str(e), user_id=user_id)
            return False
