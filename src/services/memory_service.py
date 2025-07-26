import logging
from datetime import datetime
from typing import Dict, Optional
from models.conversation import ConversationContext

logger = logging.getLogger(__name__)


class MemoryService:
    """
    In-memory conversation storage service for MVP.
    
    TODO: Extend for persistent storage (Redis, PostgreSQL, etc.) in production.
    """
    
    def __init__(self):
        # Simple dict-based storage for MVP
        self._conversations: Dict[str, ConversationContext] = {}
        logger.info("MemoryService initialized with in-memory storage")
    
    def get_conversation_context(self, user_id: str) -> ConversationContext:
        """
        Get or create a conversation context for the user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            ConversationContext for the user
        """
        if user_id not in self._conversations:
            self._conversations[user_id] = ConversationContext(user_id=user_id)
            logger.info(f"Created new conversation context for user: {user_id}")
        
        return self._conversations[user_id]
    
    def update_conversation_context(self, user_id: str, context: ConversationContext) -> None:
        """
        Update the conversation context for a user.
        
        Args:
            user_id: Unique identifier for the user
            context: Updated conversation context
        """
        self._conversations[user_id] = context
        logger.debug(f"Updated conversation context for user: {user_id}")
    
    def log_conversation_end(self, user_id: str, session_start_time: datetime) -> None:
        """
        Log the end of a conversation session.
        
        Args:
            user_id: Unique identifier for the user
            session_start_time: When the session started
        """
        if user_id in self._conversations:
            context = self._conversations[user_id]
            session_duration = datetime.now() - session_start_time
            logger.info(
                f"Conversation ended for user: {user_id}, "
                f"Duration: {session_duration}, "
                f"Messages: {len(context.messages)}, "
                f"Risk Level: {context.risk_level}"
            )
            
            # TODO: Implement session archival for long-term storage
            # For now, we keep the conversation in memory
        else:
            logger.warning(f"Attempted to log conversation end for unknown user: {user_id}")
    
    def clear_conversation(self, user_id: str) -> bool:
        """
        Clear conversation history for a user (for testing or privacy).
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            True if conversation was cleared, False if user not found
        """
        if user_id in self._conversations:
            del self._conversations[user_id]
            logger.info(f"Cleared conversation for user: {user_id}")
            return True
        return False
    
    def get_active_conversations_count(self) -> int:
        """Get the number of active conversations."""
        return len(self._conversations)