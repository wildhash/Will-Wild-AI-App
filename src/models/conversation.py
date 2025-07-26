from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Represents a single message in a conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    mood_detected: Optional[str] = None  # Detected mood for this message
    mood_confidence: Optional[float] = None  # Confidence score for mood detection


class ConversationContext(BaseModel):
    """Represents the context of a conversation with a user."""
    user_id: str
    messages: List[Message] = []
    session_start_time: datetime = Field(default_factory=datetime.now)
    risk_level: str = "low"  # low, medium, high, critical
    current_mood: str = "neutral"  # Current detected mood
    mood_analytics: Dict[str, Any] = Field(default_factory=dict)  # Mood trends and analytics
    
    def add_message(self, role: str, content: str, mood_detected: Optional[str] = None, mood_confidence: Optional[float] = None):
        """Add a message to the conversation with optional mood information."""
        message = Message(
            role=role, 
            content=content,
            mood_detected=mood_detected,
            mood_confidence=mood_confidence
        )
        self.messages.append(message)
        
        # Update current mood if detected
        if mood_detected:
            self.current_mood = mood_detected


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    user_id: str
    message: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    risk_level: str = "low"
    session_id: Optional[str] = None
    mood_detected: Optional[str] = None  # Current detected mood
    mood_confidence: Optional[float] = None  # Confidence in mood detection
    mood_analytics: Optional[Dict[str, Any]] = None  # Mood trends and analytics