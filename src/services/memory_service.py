import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional
from models.conversation import ConversationContext

logger = logging.getLogger(__name__)


class MemoryService:
    """
    In-memory conversation storage service for MVP with privacy and cleanup features.
    
    TODO: Extend for persistent storage (Redis, PostgreSQL, etc.) in production.
    TODO: Implement encryption for sensitive conversation data.
    """
    
    def __init__(self, max_conversations: int = 1000, max_messages_per_conversation: int = 100):
        # Simple dict-based storage for MVP with privacy-focused session IDs
        self._conversations: Dict[str, ConversationContext] = {}
        self._user_id_to_hash: Dict[str, str] = {}  # For session management
        self.max_conversations = max_conversations
        self.max_messages_per_conversation = max_messages_per_conversation
        logger.info(f"MemoryService initialized with max {max_conversations} conversations, "
                   f"{max_messages_per_conversation} messages each")
    
    def _hash_user_id(self, user_id: str) -> str:
        """Generate a privacy-safe hash for user identification."""
        if user_id not in self._user_id_to_hash:
            # Create a consistent hash for the session
            self._user_id_to_hash[user_id] = hashlib.sha256(user_id.encode()).hexdigest()[:16]
        return self._user_id_to_hash[user_id]
    
    def get_conversation_context(self, user_id: str) -> ConversationContext:
        """
        Get or create a conversation context for the user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            ConversationContext for the user
        """
        # Use privacy-safe hash for internal storage
        session_hash = self._hash_user_id(user_id)
        
        if session_hash not in self._conversations:
            # Create new conversation with original user_id for context but hashed storage
            self._conversations[session_hash] = ConversationContext(user_id=user_id)
            logger.info(f"Created new conversation context for session: {session_hash}")
            
            # Enforce conversation limits
            self._enforce_conversation_limits()
        
        return self._conversations[session_hash]
    
    def update_conversation_context(self, user_id: str, context: ConversationContext) -> None:
        """
        Update the conversation context for a user.
        
        Args:
            user_id: Unique identifier for the user
            context: Updated conversation context
        """
        session_hash = self._hash_user_id(user_id)
        
        # Enforce message limits per conversation
        if len(context.messages) > self.max_messages_per_conversation:
            # Keep only the most recent messages
            context.messages = context.messages[-self.max_messages_per_conversation:]
            logger.info(f"Trimmed conversation messages for session {session_hash} to {self.max_messages_per_conversation}")
        
        self._conversations[session_hash] = context
        logger.debug(f"Updated conversation context for session: {session_hash}")
    
    def _enforce_conversation_limits(self) -> None:
        """Enforce maximum number of active conversations."""
        if len(self._conversations) > self.max_conversations:
            # Remove oldest conversations based on last activity
            sorted_conversations = sorted(
                self._conversations.items(),
                key=lambda x: x[1].messages[-1].timestamp if x[1].messages else x[1].session_start_time
            )
            
            # Remove oldest conversations
            conversations_to_remove = len(self._conversations) - self.max_conversations
            for i in range(conversations_to_remove):
                session_hash, context = sorted_conversations[i]
                del self._conversations[session_hash]
                # Also clean up the user_id mapping
                user_id_to_remove = None
                for uid, hash_val in self._user_id_to_hash.items():
                    if hash_val == session_hash:
                        user_id_to_remove = uid
                        break
                if user_id_to_remove:
                    del self._user_id_to_hash[user_id_to_remove]
                    
                logger.info(f"Removed old conversation {session_hash} due to memory limits")
    
    def log_conversation_end(self, user_id: str, session_start_time: datetime) -> None:
        """
        Log the end of a conversation session.
        
        Args:
            user_id: Unique identifier for the user
            session_start_time: When the session started
        """
        session_hash = self._hash_user_id(user_id)
        
        if session_hash in self._conversations:
            context = self._conversations[session_hash]
            session_duration = datetime.now() - session_start_time
            
            # Privacy-focused logging (no personal data)
            logger.info(
                f"Conversation ended for session: {session_hash}, "
                f"Duration: {session_duration}, "
                f"Messages: {len(context.messages)}, "
                f"Risk Level: {context.risk_level}, "
                f"Final Mood: {context.current_mood}"
            )
            
            # TODO: Implement session archival for long-term storage
            # TODO: Add conversation analytics for insights
            # For now, we keep the conversation in memory but mark it as ended
            
        else:
            logger.warning(f"Attempted to log conversation end for unknown session")
    
    def clear_conversation(self, user_id: str) -> bool:
        """
        Clear conversation history for a user (for testing or privacy).
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            True if conversation was cleared, False if user not found
        """
        session_hash = self._hash_user_id(user_id)
        
        if session_hash in self._conversations:
            del self._conversations[session_hash]
            # Clean up user_id mapping
            if user_id in self._user_id_to_hash:
                del self._user_id_to_hash[user_id]
            logger.info(f"Cleared conversation for session: {session_hash}")
            return True
        return False
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clean up expired conversation sessions.
        
        Args:
            max_age_hours: Maximum age in hours for keeping sessions
            
        Returns:
            Number of sessions cleaned up
        """
        try:
            current_time = datetime.now()
            sessions_cleaned = 0
            sessions_to_remove = []
            
            for session_hash, context in self._conversations.items():
                # Determine session age based on last activity
                if context.messages:
                    last_activity = context.messages[-1].timestamp
                else:
                    last_activity = context.session_start_time
                
                age_hours = (current_time - last_activity).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    sessions_to_remove.append(session_hash)
            
            # Remove expired sessions
            for session_hash in sessions_to_remove:
                del self._conversations[session_hash]
                # Clean up user_id mapping
                user_id_to_remove = None
                for uid, hash_val in self._user_id_to_hash.items():
                    if hash_val == session_hash:
                        user_id_to_remove = uid
                        break
                if user_id_to_remove:
                    del self._user_id_to_hash[user_id_to_remove]
                
                sessions_cleaned += 1
            
            if sessions_cleaned > 0:
                logger.info(f"Cleaned up {sessions_cleaned} expired conversation sessions")
            
            return sessions_cleaned
            
        except Exception as e:
            logger.error(f"Error during session cleanup: {str(e)}")
            return 0
    
    def get_active_conversations_count(self) -> int:
        """Get the number of active conversations."""
        return len(self._conversations)
    
    def get_session_stats(self) -> Dict:
        """Get statistics about current sessions (privacy-safe)."""
        try:
            total_messages = sum(len(context.messages) for context in self._conversations.values())
            
            # Calculate mood distribution across all sessions
            mood_distribution = {}
            risk_distribution = {}
            
            for context in self._conversations.values():
                mood = context.current_mood
                risk = context.risk_level
                
                mood_distribution[mood] = mood_distribution.get(mood, 0) + 1
                risk_distribution[risk] = risk_distribution.get(risk, 0) + 1
            
            return {
                "active_sessions": len(self._conversations),
                "total_messages": total_messages,
                "average_messages_per_session": total_messages / len(self._conversations) if self._conversations else 0,
                "mood_distribution": mood_distribution,
                "risk_distribution": risk_distribution
            }
            
        except Exception as e:
            logger.error(f"Error calculating session stats: {str(e)}")
            return {"error": "stats_unavailable"}