import logging
import uuid
from datetime import datetime
from typing import Dict, Optional, List
from models.conversation import ConversationContext

logger = logging.getLogger(__name__)


class MemoryService:
    """
    In-memory conversation storage service for MVP with session support.
    
    TODO: Extend for persistent storage (Redis, PostgreSQL, etc.) in production.
    """
    
    def __init__(self):
        # Session-based storage for conversations
        self._sessions: Dict[str, ConversationContext] = {}
        # User to session mapping for backward compatibility
        self._user_sessions: Dict[str, List[str]] = {}
        logger.info("MemoryService initialized with session-based storage")
    
    def create_session(self, user_id: str) -> str:
        """
        Create a new conversation session for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Session ID for the new session
        """
        session_id = str(uuid.uuid4())
        context = ConversationContext(user_id=user_id, session_id=session_id)
        
        self._sessions[session_id] = context
        
        # Track user sessions for backward compatibility
        if user_id not in self._user_sessions:
            self._user_sessions[user_id] = []
        self._user_sessions[user_id].append(session_id)
        
        logger.info(f"Created new session {session_id} for user: {user_id}")
        return session_id
    
    def get_session_context(self, session_id: str) -> Optional[ConversationContext]:
        """
        Get conversation context for a specific session.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            ConversationContext for the session or None if not found
        """
        return self._sessions.get(session_id)
    
    def get_conversation_context(self, user_id: str) -> ConversationContext:
        """
        Get or create a conversation context for the user (backward compatibility).
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            ConversationContext for the user
        """
        # Check if user has existing sessions
        if user_id in self._user_sessions and self._user_sessions[user_id]:
            # Return the most recent session
            latest_session_id = self._user_sessions[user_id][-1]
            return self._sessions[latest_session_id]
        
        # Create new session for backward compatibility
        session_id = self.create_session(user_id)
        return self._sessions[session_id]
    
    def update_conversation_context(self, user_id: str, context: ConversationContext) -> None:
        """
        Update the conversation context for a user (backward compatibility).
        
        Args:
            user_id: Unique identifier for the user
            context: Updated conversation context
        """
        if hasattr(context, 'session_id') and context.session_id:
            self._sessions[context.session_id] = context
            logger.debug(f"Updated conversation context for session: {context.session_id}")
        else:
            # Fallback for old-style contexts without session_id
            if user_id in self._user_sessions and self._user_sessions[user_id]:
                latest_session_id = self._user_sessions[user_id][-1]
                self._sessions[latest_session_id] = context
                logger.debug(f"Updated conversation context for user: {user_id}")
    
    def update_session_context(self, session_id: str, context: ConversationContext) -> None:
        """
        Update the conversation context for a specific session.
        
        Args:
            session_id: Unique identifier for the session
            context: Updated conversation context
        """
        self._sessions[session_id] = context
        logger.debug(f"Updated conversation context for session: {session_id}")
    
    def log_conversation_end(self, user_id: str, session_start_time: datetime) -> None:
        """
        Log the end of a conversation session.
        
        Args:
            user_id: Unique identifier for the user
            session_start_time: When the session started
        """
        # Find session by user_id for backward compatibility
        if user_id in self._user_sessions and self._user_sessions[user_id]:
            latest_session_id = self._user_sessions[user_id][-1]
            if latest_session_id in self._sessions:
                context = self._sessions[latest_session_id]
                session_duration = datetime.now() - session_start_time
                logger.info(
                    f"Conversation ended for user: {user_id}, session: {latest_session_id}, "
                    f"Duration: {session_duration}, "
                    f"Messages: {len(context.messages)}, "
                    f"Risk Level: {context.risk_level}"
                )
            else:
                logger.warning(f"Session {latest_session_id} not found for user: {user_id}")
        else:
            logger.warning(f"No sessions found for user: {user_id}")
    
    def log_session_end(self, session_id: str) -> None:
        """
        Log the end of a specific session.
        
        Args:
            session_id: Unique identifier for the session
        """
        if session_id in self._sessions:
            context = self._sessions[session_id]
            session_duration = datetime.now() - context.session_start_time
            logger.info(
                f"Session ended: {session_id}, user: {context.user_id}, "
                f"Duration: {session_duration}, "
                f"Messages: {len(context.messages)}, "
                f"Risk Level: {context.risk_level}"
            )
        else:
            logger.warning(f"Attempted to log end for unknown session: {session_id}")
    
    def clear_conversation(self, user_id: str) -> bool:
        """
        Clear conversation history for a user (for testing or privacy).
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            True if conversation(s) were cleared, False if user not found
        """
        if user_id in self._user_sessions:
            # Clear all sessions for the user
            for session_id in self._user_sessions[user_id]:
                if session_id in self._sessions:
                    del self._sessions[session_id]
            del self._user_sessions[user_id]
            logger.info(f"Cleared all conversations for user: {user_id}")
            return True
        return False
    
    def clear_session(self, session_id: str) -> bool:
        """
        Clear a specific session.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            True if session was cleared, False if not found
        """
        if session_id in self._sessions:
            context = self._sessions[session_id]
            user_id = context.user_id
            
            # Remove from sessions
            del self._sessions[session_id]
            
            # Remove from user sessions mapping
            if user_id in self._user_sessions:
                self._user_sessions[user_id] = [
                    sid for sid in self._user_sessions[user_id] if sid != session_id
                ]
                if not self._user_sessions[user_id]:
                    del self._user_sessions[user_id]
            
            logger.info(f"Cleared session: {session_id}")
            return True
        return False
    
    def get_active_conversations_count(self) -> int:
        """Get the number of active sessions."""
        return len(self._sessions)
    
    def get_user_sessions(self, user_id: str) -> List[str]:
        """
        Get all session IDs for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            List of session IDs for the user
        """
        return self._user_sessions.get(user_id, [])
    
    def append_message(self, session_id: str, role: str, content: str) -> bool:
        """
        Append a message to a session's conversation history.
        
        Args:
            session_id: Unique identifier for the session
            role: Role of the message sender (user/assistant)
            content: Message content
            
        Returns:
            True if message was appended successfully
        """
        if session_id in self._sessions:
            self._sessions[session_id].add_message(role, content)
            return True
        return False
    
    def fetch_chat_history(self, session_id: str) -> List[dict]:
        """
        Fetch chat history for a session.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            List of message dictionaries
        """
        if session_id in self._sessions:
            context = self._sessions[session_id]
            return [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in context.messages
            ]
        return []