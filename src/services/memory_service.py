import logging
from datetime import datetime
from typing import Dict, Optional, List
from models.conversation import ConversationContext, MoodData
from services.mood_analysis_service import MoodAnalysisService

logger = logging.getLogger(__name__)


class MemoryService:
    """
    In-memory conversation storage service with mood tracking for MVP.
    
    TODO: Extend for persistent storage (Redis, PostgreSQL, etc.) in production.
    TODO: Add mood data persistence and historical analysis capabilities.
    """
    
    def __init__(self):
        # Simple dict-based storage for MVP
        self._conversations: Dict[str, ConversationContext] = {}
        # Initialize mood analysis service
        self.mood_analyzer = MoodAnalysisService()
        logger.info("MemoryService initialized with in-memory storage and mood analysis")
    
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
    
    def add_user_message_with_mood(self, user_id: str, message: str) -> MoodData:
        """
        Add a user message with mood analysis to the conversation.
        
        Args:
            user_id: Unique identifier for the user
            message: User's message content
            
        Returns:
            MoodData with detected mood information
        """
        context = self.get_conversation_context(user_id)
        
        # Analyze mood of the user message
        mood_data = self.mood_analyzer.analyze_mood(message)
        
        # Add message with mood data
        context.add_message("user", message, mood_data)
        
        logger.debug(f"Added user message with mood '{mood_data.mood}' "
                    f"(confidence: {mood_data.confidence}) for user: {user_id}")
        
        return mood_data
    
    def add_assistant_message(self, user_id: str, message: str) -> None:
        """
        Add an assistant message to the conversation.
        
        Args:
            user_id: Unique identifier for the user
            message: Assistant's message content
        """
        context = self.get_conversation_context(user_id)
        context.add_message("assistant", message)
        
        logger.debug(f"Added assistant message for user: {user_id}")
    
    def get_mood_timeline(self, user_id: str) -> List[MoodData]:
        """
        Get the mood timeline for a user's session.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            List of MoodData from user messages in chronological order
        """
        if user_id not in self._conversations:
            return []
        
        context = self._conversations[user_id]
        return context.get_mood_timeline()
    
    def get_session_mood_summary(self, user_id: str) -> Dict:
        """
        Get aggregated mood summary for a user's session.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary with mood summary statistics
        """
        mood_timeline = self.get_mood_timeline(user_id)
        return self.mood_analyzer.calculate_session_mood_summary(mood_timeline)
    
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