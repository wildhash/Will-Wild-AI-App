from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Represents a single message in a conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ConversationContext(BaseModel):
    """Represents the context of a conversation with a user."""
    user_id: str
    session_id: Optional[str] = None
    messages: List[Message] = []
    session_start_time: datetime = Field(default_factory=datetime.now)
    risk_level: str = "low"  # low, medium, high, critical
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation."""
        self.messages.append(Message(role=role, content=content))


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    user_id: str
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    risk_level: str = "low"
    session_id: Optional[str] = None


class SessionCreateRequest(BaseModel):
    """Request model for creating a new session."""
    user_id: str


class SessionResponse(BaseModel):
    """Response model for session endpoints."""
    session_id: str
    user_id: str
    created_at: str
    message_count: int
    risk_level: str
    messages: List[dict] = []